#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""requests-htmlでスクレイピング

requestsでスクレイピングできないページのスクレイピング

- 参考資料
   - https://gammasoft.jp/blog/how-to-download-web-page-created-javascript/
   - https://docs.python-requests.org/projects/requests-html/en/latest/
   - https://commte.net/7628
   - https://qiita.com/uitspitss/items/f131ea79dffd58bc01ae
   - https://computer.masas-record-storage-container.com/2021/03/01/requestshtml/

- Documents
   - https://requests.readthedocs.io/projects/requests-html/en/latest/

- requests-htmlのGitHub
   - https://github.com/kennethreitz/requests-html
"""
import copy
import json
from dataclasses import dataclass, field
import pyperclip
from requests_html import HTMLSession
from requests.exceptions import RequestException


def is_num(s: str) -> bool:
    """数値かどうかを判定する

    Args:
        s: 判定対象の文字列

    Returns:
        True: 数値の場合, False: 数値でない場合
    """
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True


@dataclass(frozen=True)
class TenkiValue:
    """クローリング値オブジェクト"""
    target_url: str
    css_root: str
    css_selectors: dict
    attrs: dict
    title: str
    forecasts: dict = field(default_factory=dict)
    counters: dict = field(default_factory=dict)


class Tenki:
    """クローリングユーティリティ

    指定のサイトを読み込み、指定のCSSセレクタ(css_selectors)と属性でクローリング(attrs)し、クローリング結果でTenkiValueを生成する

    Attributes:
        tenki_value: TenkiValueオブジェクト
        target_url: 対象サイトのURL
        css_root: スクレイピングルートCSSセレクタ
        css_selectors: スクレイピングCSSセレクタ辞書
        attrs: スクレイピング属性辞書
    """
    tenki_value: TenkiValue = None
    target_url: str = None
    css_root: str = None
    css_selectors: dict = None
    attrs: dict = None

    def __init__(
            self,
            target_value: TenkiValue | str = None,
            css_root: str = None,
            css_selectors: dict = None,
            attrs: dict = None
    ) -> None:
        """コンストラクタ

        Args:
            target_value: 対象サイトURL文字列、またはTenkiValueオブジェクト
            css_root: スクレイピングルートCSSセレクタ
            css_selectors: スクレイピングCSSセレクタ辞書
            attrs: スクレイピング属性辞書
        """
        if target_value is not None:
            if isinstance(target_value, TenkiValue):
                tenki_value = target_value
                self.tenki_value = tenki_value
                if tenki_value.target_url is not None:
                    self.target_url = tenki_value.target_url
                if tenki_value.css_root is not None:
                    self.css_root = tenki_value.css_root
                if tenki_value.css_selectors is not None:
                    self.css_selectors = tenki_value.css_selectors
                if tenki_value.attrs is not None:
                    self.attrs = tenki_value.attrs
            else:
                if isinstance(target_value, str):
                    self.target_url = target_value
                    if css_root is not None:
                        self.css_root = css_root
                        if css_selectors is not None:
                            self.css_selectors = css_selectors
                            if attrs is not None:
                                self.attrs = attrs
                                self.request()

    def special_func_temp(self):
        """特別製

        temp_itemのjava-scriptを解析して、
        データとカウンターを整える（元のデータを書き換える）
        """
        temp_item_forecasts = []
        temp_item_counters = []
        count = 0
        left_find = 'data: ['
        sp_key = 'temp_item'
        # 初日の予報なしに対応
        for value in self.tenki_value.counters[sp_key]:
            if value:
                break
            else:
                temp_item_counters.append(value)
        # スクリプトの中から気温を探して登録しなおす
        for value in self.tenki_value.forecasts[sp_key]:
            left = value.find(left_find) + len(left_find)
            right = left + value[left:].find(']')
            new_list = value[left:right].split(',')
            for item in new_list:
                if is_num(item):
                    temp_item_forecasts.append(str(item) + "℃")
                    count += 1
            temp_item_counters.append(count)
        # 末日の予報なしに対応
        pre = -1
        for value in self.tenki_value.counters[sp_key]:
            if value == pre:
                temp_item_counters.append(count)
            pre = value
        self.tenki_value.forecasts[sp_key] = temp_item_forecasts
        self.tenki_value.counters[sp_key] = temp_item_counters

    def create_LINE_BOT_TOBA_format(self):
        """時間毎の天気予報配列を作る

        Returns:
            dict: 天気予報配列
        """
        forecasts = self.get_result_forecasts()
        counters = self.get_result_counters()
        data = {}

        # 日付列作成
        sp_key = 'forecast_item'  # 日付以外で数が少ない項目を使用する
        target_key = 'days_item'
        data[target_key] = []
        sub_key = 'week_item'
        data[sub_key] = []
        pre = 0
        for index in range(len(counters[sp_key])):
            num = counters[sp_key][index] - pre
            if num:  # 0または、増加していない時以外
                for i in range(num):
                    num1 = counters[target_key][index]
                    _buff = forecasts[target_key][num1 - 1]
                    left = _buff.find('(')
                    right = _buff.find(')')
                    data[target_key].append(_buff[:left])
                    data[sub_key].append(_buff[left + 1:right])
                pre = counters[sp_key][index]

        # 時間列作成
        cycle = 4
        target_key = 'time_item'
        data[target_key] = []
        pre_sp_key = 0
        pre_target_key = 0
        for index in range(len(counters[sp_key])):
            num = counters[sp_key][index] - pre_sp_key
            start = pre_target_key + cycle - num
            end = counters[target_key][index] - 1
            if num:
                for i in range(start, end):
                    _buff = forecasts[target_key][i] + '時-' + forecasts[target_key][i + 1] + '時'
                    data[target_key].append(_buff)
                pre_target_key = counters[target_key][index]
                pre_sp_key = counters[sp_key][index]

        # 天気、湿度、降水量列作成
        target_keys = {'天気': 'forecast_item', '温度': 'prob_precip_item', '降水量': 'precip_item'}
        for target_key in target_keys.values():
            data[target_key] = []
            pre_target_key = 0
            for index in range(len(counters[sp_key])):
                num = counters[target_key][index] - pre_target_key
                start = pre_target_key
                end = counters[target_key][index]
                if num:
                    for i in range(start, end):
                        _buff = forecasts[target_key][i]
                        data[target_key].append(_buff)
                    pre_target_key = counters[target_key][index]

        # 気温、風向、風力列作成
        target_keys = {'気温': 'temp_item', '風向': 'wind_item_blow', '風力': 'wind_item_speed'}
        for target_key in target_keys.values():
            data[target_key] = []
            pre_sp_key = 0
            pre_target_key = 0
            for index in range(len(counters[sp_key])):
                num = counters[sp_key][index] - pre_sp_key
                start = pre_target_key
                end = counters[target_key][index] - 1
                if num:
                    for i in range(start, end):
                        _buff = forecasts[target_key][i] + '-' + forecasts[target_key][i + 1]
                        data[target_key].append(_buff)
                    pre_target_key = counters[target_key][index]
                    pre_sp_key = counters[sp_key][index]

        return data

    def get_value_objects(self):
        """値オブジェクトを取得する

        Returns:
            TenkiValue: 値オブジェクト
        """
        return copy.deepcopy(self.tenki_value)

    def get_result_forecasts(self):
        """クローリング結果を取得する

        Returns:
            dict: クローリング結果
        """
        return copy.deepcopy(self.tenki_value.forecasts)

    def get_result_counters(self):
        """クローリング結果を取得する

        Returns:
            dict: クローリング結果
        """
        return copy.deepcopy(self.tenki_value.counters)

    def get_title(self):
        """対象サイトタイトルを取得する

        Returns:
            str: 対象サイトタイトル
        """
        return self.tenki_value.title

    def request(self) -> bool:
        """target_urlに接続し、スクレイピングを実行してtenki_valueを更新する

        Returns:
            True: 成功, False: 失敗

        Raises:
            RequestException: リクエストエラーが発生した場合
        """
        try:
            script = """
                () => {
                    return {
                        width: document.documentElement.clientWidth,
                        height: document.documentElement.clientHeight,
                        deviceScaleFactor: window.devicePixelRatio,
                    }
                }
            """
            forecasts = {}
            counters = {}
            session = HTMLSession()
            response = session.get(self.target_url)
            # Chromiumで応答を再読み込みし、JavaScriptを実行して、HTMLコンテンツを更新されたバージョンに置き換える
            response.html.render(script=script,  # ページ読み込み時に実行するJavaScript
                                 reload=False,  # Falseの場合、コンテンツはブラウザからロードされず、メモリから提供される
                                 timeout=0,  # 0は無制限
                                 wait=5,  # ページレンダリング前のスリープ秒数
                                 sleep=15,  # ページレンダリング後のスリープ秒数
                                 )
            # スクレイピング
            title = response.html.find("html > head > title", first=True).text

            for key in self.css_selectors:
                forecasts[key] = []
                counters[key] = []
            target_rows = response.html.find(self.css_root)
            if target_rows:
                for row in target_rows:
                    for key in self.css_selectors:
                        buffer = row.find(self.css_selectors[key])
                        if not self.attrs[key] == "":
                            for buf in buffer:
                                alt = buf.attrs[self.attrs[key]]
                                if alt:
                                    forecasts[key].append(alt)
                        else:
                            for buf in buffer:
                                forecasts[key].append(buf.text)
                        counters[key].append(len(forecasts[key]))
            self.tenki_value = TenkiValue(self.target_url,
                                          self.css_root,
                                          self.css_selectors,
                                          self.attrs,
                                          title,
                                          forecasts,
                                          counters,
                                          )
        except RequestException as e:
            print(f"リクエストエラー: {e}")
            return False
        except Exception as e:
            print(f"スクレイピングエラー:{e}")
            return False

        return True


    def create_save_text(self):
        """保存用文字列の作成

        Returns:
            str: 保存用文字列の作成
        """
        buff = self.tenki_value.target_url + '\n'  # サイトURL追加
        buff += self.tenki_value.css_root + '\n'  # ルートcssセレクタ追加
        buff += json.dumps(self.tenki_value.css_selectors, ensure_ascii=False) + '\n'  # cssセレクタ追加
        buff += json.dumps(self.tenki_value.attrs, ensure_ascii=False) + '\n'  # 属性追加
        buff += self.tenki_value.title + '\n'  # タイトル追加
        buff += json.dumps(self.tenki_value.forecasts, ensure_ascii=False) + '\n'  # 画像URL追加
        buff += json.dumps(self.tenki_value.counters, ensure_ascii=False) + '\n'  # 画像URL追加
        return buff

    def clip_copy(self):
        """クローリング結果をクリップボードにコピーする

        Returns:
            bool: 成功/失敗=True/False
        """
        if self.tenki_value is None:
            return False
        buff = self.create_save_text()
        pyperclip.copy(buff)  # クリップボードへのコピー
        return True

    def save_text(self, save_path):
        """データをファイルに、以下の独自フォーマットで保存する
            * 処理対象サイトURL
            * ルートCSSセレクタ
            * CSSセレクタ
            * 属性
            * タイトル
            * クローリング結果

        Args:
            save_path (str): セーブする独自フォーマットなファイルのパス

        Returns:
            bool: 成功/失敗=True/False
        """
        if self.tenki_value is None:
            return False
        with open(save_path, 'w', encoding='utf-8') as work_file:
            buff = self.create_save_text()
            work_file.write(buff)  # ファイルへの保存
            return True

    def load_text(self, load_path):
        """独自フォーマットなファイルからデータを読み込む

        Args:
            load_path (str): ロードする独自フォーマットなファイルのパス

        Returns:
            bool: 成功/失敗=True/False
        """
        with open(load_path, 'r', encoding='utf-8') as work_file:
            buff = work_file.readlines()
            self.target_url = buff[0].rstrip('\n')
            del buff[0]
            self.css_root = buff[0].rstrip('\n')
            del buff[0]
            self.css_selectors = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            self.attrs = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            title = buff[0].rstrip('\n')
            del buff[0]
            forecasts: dict = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            counters: dict = json.loads(buff[0].rstrip('\n'))
            self.tenki_value = TenkiValue(self.target_url,
                                          self.css_root,
                                          self.css_selectors,
                                          self.attrs,
                                          title,
                                          forecasts,
                                          counters,
                                          )
            return True
