#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
クローリング
    * 指定サイト(site_url)をセレクタ(site_selectors)でクローリングする(ChromeDriverを使用)
    * クローリング結果を、crawling_file_pathに保存する
    * crawling_file_pathのpage_urlsは、スクレイピングする対象urlリストである
    * crawling_file_pathのexclusion_urlsは、スクレイピングの除外urlリストである
    * zip保存まで終わると、page_urlsからexclusion_urlsにurlを移す
    * セレクタを、image_urlで定義すると、crawling_url_deploymentでスクレイピングして末尾画像URLの展開URLでダウンロードして、zipに保存する
    * セレクタを、image_urlsで定義すると、crawling_urlsでスクレイピングしてダウンロードして、zipに保存する
"""
import os
import sys
import copy
import inspect
import json
import datetime
import time
from dataclasses import dataclass
from typing import Union, Optional
import helper.chromeDriver
import helper.webFile
import helper.webFileList
import helper.line_message_api
import helper.slack_message_api
import helper.status


@dataclass(frozen=True)
class CrawlingValue:
    """Crawlingの値オブジェクトクラス

    Attributes:
        site_url (str): サイトURL
        site_selectors (Dict[str, str]): サイトセレクタ。キーはアイテム名、値はCSSセレクタ
        crawling_items (Dict[str, List[str]]): クローリングアイテム。キーはアイテムの種類（例：'page_urls'）、値はURLのリスト
        crawling_file_path (str): クローリングファイルパス

    Raises:
        ValueError: 各属性が不正な値（None、空文字列、不正な型）の場合
    """
    site_url: str = None
    site_selectors: dict = None
    crawling_items: dict = None
    crawling_file_path: str = None

    def __init__(self, site_url, site_selectors, crawling_items, crawling_file_path):
        """完全コンストラクタパターン"""
        if not site_url:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:site_url=None")
        if not site_selectors:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:site_selectors=None")
        if crawling_items is None:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:crawling_items=None")
        if not crawling_file_path:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:crawling_file_path=None")
        if not isinstance(site_url, str):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:site_urlがstrではない")
        if not isinstance(site_selectors, dict):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:site_selectorsがdictではない")
        if not isinstance(crawling_items, dict):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:crawling_itemsがdictではない")
        if not isinstance(crawling_file_path, str):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:crawling_file_pathがstrではない")
        object.__setattr__(self, "site_url", site_url)
        object.__setattr__(self, "site_selectors", site_selectors)
        object.__setattr__(self, "crawling_items", crawling_items)
        object.__setattr__(self, "crawling_file_path", crawling_file_path)


class Crawling:
    """クローリングクラス

    指定されたサイトをクローリングし、結果をファイルに保存します
    """
    URLS_TARGET = "page_urls"
    URLS_EXCLUSION = "exclusion_urls"
    URLS_FAILURE = "failure_urls"
    value_object: CrawlingValue = None
    site_selectors: dict = None
    crawling_items: dict = {URLS_TARGET: [], URLS_EXCLUSION: [], URLS_FAILURE: []}
    crawling_file_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           '../crawling_list.txt').replace(os.sep, '/')

    def __init__(self,
                 value_object=None,
                 site_selectors=None,
                 crawling_items=None,
                 crawling_file_path=crawling_file_path):
        if value_object:
            if isinstance(value_object, CrawlingValue):
                value_object = copy.deepcopy(value_object)
                self.value_object = value_object
                self.load_text()
                self.save_text()
            elif isinstance(value_object, str):
                if site_selectors:
                    site_selectors = copy.deepcopy(site_selectors)
                    site_url = value_object
                    if crawling_items is None:
                        crawling_items = Crawling.crawling_items
                    self.value_object = CrawlingValue(site_url,
                                                      site_selectors,
                                                      crawling_items,
                                                      crawling_file_path)
                    self.load_text()
                    self.save_text()
                else:
                    raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                                     f"引数エラー:site_selectors=None")
            elif isinstance(value_object, dict):
                site_selectors = copy.deepcopy(value_object)
                self.load_text(site_selectors, crawling_file_path)
                self.save_text()
            else:
                raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                                 f"引数エラー:value_objectが無効な型")
        else:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:value_object=None")

    @staticmethod
    def dict_merge(dict1, dict2):
        """dict2をdict1にマージする。dictは値がlistであること。list内の重複は削除。list内の順序を維持"""
        dict1 = copy.deepcopy(dict1)
        dict2 = copy.deepcopy(dict2)
        for key, value in dict2.items():
            if key in dict1:
                dict1[key].extend(value)
                dict1[key] = list(dict.fromkeys(dict1[key]))
            else:
                dict1[key] = value
        return dict1

    @staticmethod
    def take_out(items, item_name):
        """crawling_itemsから指定のitemを取り出す"""
        ret_value = None
        if item_name in items:
            ret_value = copy.deepcopy(items[item_name])
        if ret_value and isinstance(ret_value, list):
            if len(ret_value) == 1:
                # listの中身が一つしかない時
                ret_value = ret_value[0]
        return ret_value

    @staticmethod
    def validate_title(items: dict, title: str, title_sub: str):
        title = Crawling.take_out(items, title)
        title_sub = Crawling.take_out(items, title_sub)
        if isinstance(title, list) and len(title) > 0:
            title = title[0]
        if isinstance(title_sub, list) and len(title_sub) > 0:
            title_sub = title_sub[0]
        if not title:
            if not title_sub:
                # タイトルが得られない時は、タイトルを日時文字列にする
                now = datetime.datetime.now()
                title = f'{now:%Y%m%d_%H%M%S}'
            else:
                title = title_sub
        return helper.chromeDriver.ChromeDriver.fixed_file_name(title)

    @staticmethod
    def download_chrome_driver(web_file_list):
        """selenium chromeDriverを用いて、画像をデフォルトダウンロードフォルダにダウンロードして、指定のフォルダに移動する
        """
        chromedriver = helper.chromeDriver.ChromeDriver()
        for url, path in zip(web_file_list.get_url_list(), web_file_list.get_path_list()):
            chromedriver.download_image(url, path)

    @staticmethod
    def scraping(url, selectors):
        """ChromeDriverを使ってスクレイピングする"""
        selectors = copy.deepcopy(selectors)
        chrome_driver = helper.chromeDriver.ChromeDriver()
        try:
            # 0. 対象のURLを開く
            chrome_driver.open_current_tab(url)
            # 1. ブラウザのタイトルでロボ認証/Cloudflareブロックを判定
            # ロボ認証画面ではタイトルがドメイン名のみや "Cloudflare" になることが多い
            actual_title = chrome_driver._driver.title
            if actual_title == "nhentai.net" or "Cloudflare" in actual_title or "Attention Required!" in actual_title:
                # 「last_image_urlが不正」という文言を含めることで、呼び出し元のリトライ判定にヒットさせる
                raise ValueError(f"Bot detection detected by title: {actual_title} (last_image_urlが不正)")
            # 2. セレクタによる明示的なロボ認証要素の確認
            if 'bot_check' in selectors:
                for by, path, func in selectors['bot_check']:
                    # chrome_driver._driver を直接参照して要素を探す
                    elements = chrome_driver._driver.find_elements(by, path)
                    if len(elements) > 0:
                        raise ValueError(f"Bot check element found (last_image_urlが不正): {url}")
            # 3. スクレイピングを実行
            # ここで Selenium の "element not interactable" 等の例外が発生する可能性がある
            try:
                items = chrome_driver.scraping(selectors)
            except Exception as e:
                raise ValueError(f"Scraping interaction error: {e} (last_image_urlが不正)")
            # 指定したセレクタのすべてで結果が空（リストが空）の場合のみブロックとみなす
            # 判定対象のキー（bot_check以外）を取得
            data_keys = [k for k in selectors.keys() if k != 'bot_check']
            # すべての結果が空リスト、または None かチェック
            is_all_empty = all(not items.get(k) for k in data_keys)
            if is_all_empty:
                time.sleep(8)
                raise ValueError(f"Cloudflare blocking / Data empty (last_image_urlが不正): {url}")
            return items
        except Exception as e:
            # ここで発生した例外は上位の crawling_url_deployment メソッドの try-except へ伝播する
            raise e

    @staticmethod
    def scraping_current(chrome_driver, selectors):
        """現在ブラウザで開いているページから、指定されたセレクタを使用して情報を取得する。
        Args:
            chrome_driver (WebDriver): Selenium chrome driver
            selectors (dict): { '項目名': [(By, 'セレクタ', lambda), ...], ... } 形式の辞書
        Returns:
            dict: { '項目名': [取得した値のリスト], ... }
        """
        results = {}
        for key, selector_list in selectors.items():
            extracted_values = []
            for by_type, selector_val, extract_func in selector_list:
                try:
                    # 要素をすべて取得（見つからない場合は空リストが返るためエラーにならない）
                    elements = chrome_driver.find_elements(by_type, selector_val)
                    for el in elements:
                        # セレクタ定義にあるラムダ式を実行して値を抽出
                        value = extract_func(el)
                        if value:
                            extracted_values.append(value)
                except Exception as e:
                    print(f"  [Warning] セレクタ実行中にエラー ({key}): {e}")
            # 結果を辞書に格納
            results[key] = extracted_values
        return results

    def get_value_object(self):
        """値オブジェクトを取得する"""
        if self.value_object:
            return copy.deepcopy(self.value_object)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:value_object")

    def get_site_url(self):
        """値オブジェクトのプロパティsite_url取得"""
        if self.get_value_object().site_url:
            return copy.deepcopy(self.get_value_object().site_url)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:site_url")

    def get_site_selectors(self):
        """値オブジェクトのプロパティsite_selectors取得"""
        if self.get_value_object().site_selectors:
            return copy.deepcopy(self.get_value_object().site_selectors)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:site_selectors")

    def get_crawling_items(self):
        """値オブジェクトのプロパティcrawling_items取得"""
        if self.get_value_object().crawling_items:
            return copy.deepcopy(self.get_value_object().crawling_items)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:crawling_items")

    def get_crawling_file_path(self):
        """値オブジェクトのプロパティcrawling_file_path取得"""
        if self.get_value_object().crawling_file_path:
            return copy.deepcopy(self.get_value_object().crawling_file_path)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:crawling_file_path")

    def create_save_text(self):
        """保存用文字列の作成

        以下を保存する
            * サイトURL
            * セレクタ
            * saveファイルのフルパス
            * クローリング結果urls

        Returns:
            str: 保存用文字列の作成
        """
        __buff = json.dumps(self.get_site_url(), ensure_ascii=False) + '\n'  # サイトURL
        # TODO: selectorsはjson.dumpsでシリアライズできないオブジェクトたぶんlambdaを含んでいる。pickleでもだめらしい。
        #  代替方法dillとか https://github.com/uqfoundation/dill
        #  marshalとか検討する
        # __buff += json.dumps(self.value_object.site_selectors, ensure_ascii=False) + '\n'  # セレクタ
        if self.get_value_object().crawling_file_path:
            __buff += json.dumps(self.get_crawling_file_path(), ensure_ascii=False) + '\n'  # クローリング結果保存パス
        else:
            __buff += '\n'  # クローリング結果パス追加
        __buff += json.dumps(self.get_crawling_items(), ensure_ascii=False) + '\n'  # クローリング結果
        return __buff

    def save_text(self):
        """クローリング情報をファイルに、保存する

        Returns:
            bool: 成功/失敗=True/False
        """
        with open(self.get_crawling_file_path(), 'w', encoding='utf-8') as __work_file:
            __buff = self.create_save_text()
            __work_file.write(__buff)
        return True

    def load_text(self, selectors=None, crawling_file_path=crawling_file_path):
        """独自フォーマットなファイルからデータを読み込み、value_objectを作り直す

        Args:
            selectors (dict, optional): スクレイピングする際のセレクタリスト。デフォルトは None
            crawling_file_path (str, optional): ダウンロードフォルダのパス。デフォルトは crawling_file_path

        Returns:
            bool: 成功、True。ファイルがなかったり、ファイルが空だったら、False
        """
        if not os.path.exists(crawling_file_path):
            return False
        if os.stat(crawling_file_path).st_size == 0:
            return False
        try:
            with open(crawling_file_path, 'r', encoding='utf-8') as __work_file:
                __buff = __work_file.readlines()
                __site_url = json.loads(__buff[0].rstrip('\n'))
                # TODO: site_selectors
                # del __buff[0]
                # __selectors = json.loads(__buff[0].rstrip('\n'))
                del __buff[0]
                __crawling_file_path = json.loads(__buff[0].rstrip('\n'))
                del __buff[0]
                __crawling_items = json.loads(__buff[0].rstrip('\n'))
                del __buff[0]
                __selectors = selectors
                __crawling_items2 = None
                if self.value_object:
                    __site_url = self.get_site_url()
                    __selectors = self.get_site_selectors()
                    __crawling_items2 = self.get_crawling_items()
                if __crawling_items2:
                    __crawling_items = self.dict_merge(__crawling_items, __crawling_items2)
                __crawling_file_path = crawling_file_path
                self.value_object = CrawlingValue(__site_url, __selectors, __crawling_items, __crawling_file_path)
        except Exception as e:
            now = datetime.datetime.now().strftime('%Y%m%d%H%M')
            file_name, ext = os.path.splitext(crawling_file_path)
            backup_file_path = f"{file_name}_{now}{ext}"
            os.rename(crawling_file_path, backup_file_path)
            print(f"ファイルの読み込みに失敗しました。バックアップを作成しました: {backup_file_path}")
            print(f"エラー内容: {e}")
            return False
        return True

    def is_url_included_exclusion_list(self, url):
        """除外リストに含まれるURLならTrueを返す
        """
        crawling_items = self.get_crawling_items()
        if self.URLS_EXCLUSION in crawling_items:
            if url in crawling_items[self.URLS_EXCLUSION]:
                return True
        return False

    def move_url_from_page_urls_to_exclusion_urls(self, url):
        """ターゲットリスト(page_urls)から除外リスト(exclusion_urls)にURLを移動する
        """
        site_url = self.get_site_url()
        selectors = self.get_site_selectors()
        crawling_file_path = self.get_crawling_file_path()
        crawling_items = self.get_crawling_items()
        if self.URLS_EXCLUSION in crawling_items:
            if url not in crawling_items[self.URLS_EXCLUSION]:
                crawling_items[self.URLS_EXCLUSION].append(url)
        else:
            crawling_items[self.URLS_EXCLUSION] = [url]
        if self.URLS_TARGET in crawling_items:
            if url in crawling_items[self.URLS_TARGET]:
                crawling_items[self.URLS_TARGET].remove(url)
        self.value_object = CrawlingValue(site_url, selectors, crawling_items, crawling_file_path)
        self.save_text()

    def is_url_included_failure_list(self, url):
        """失敗リストに含まれるURLならTrueを返す
        """
        crawling_items = self.get_crawling_items()
        if self.URLS_FAILURE in crawling_items:
            if url in crawling_items[self.URLS_FAILURE]:
                return True
        return False

    def move_url_from_page_urls_to_failure_urls(self, url):
        """ターゲットリスト(page_urls)から失敗リスト(failure_urls)にURLを移動する
        """
        site_url = self.get_site_url()
        selectors = self.get_site_selectors()
        crawling_file_path = self.get_crawling_file_path()
        crawling_items = self.get_crawling_items()
        if self.URLS_FAILURE in crawling_items:
            if url not in crawling_items[self.URLS_FAILURE]:
                crawling_items[self.URLS_FAILURE].append(url)
        else:
            crawling_items[self.URLS_FAILURE] = [url]
        if self.URLS_TARGET in crawling_items:
            if url in crawling_items[self.URLS_TARGET]:
                crawling_items[self.URLS_TARGET].remove(url)
        self.value_object = CrawlingValue(site_url, selectors, crawling_items, crawling_file_path)
        self.save_text()

    def marge_crawling_items(self):
        """crawling_itemsのpage_urlsにexclusion_urlsがあったら削除する"""
        crawling_items = self.get_crawling_items()
        page_urls = []
        if self.URLS_TARGET in crawling_items:
            page_urls = crawling_items[self.URLS_TARGET]
        for page_url in page_urls:
            print(page_url)
            if self.is_url_included_exclusion_list(page_url):
                self.move_url_from_page_urls_to_exclusion_urls(page_url)
                continue
            if self.is_url_included_failure_list(page_url):
                self.move_url_from_page_urls_to_failure_urls(page_url)
                continue

    def crawling_url_deployment(self, page_selectors, image_selectors, notification_id=""):
        chrome_instance = helper.chromeDriver.ChromeDriver()
        driver = chrome_instance._driver
        crawling_items = self.get_crawling_items()
        page_urls = crawling_items.get(self.URLS_TARGET, [])
        total_pages = len(page_urls)
        max_retries = 3
        retry_delay = 10
        for i, page_url in enumerate(page_urls):
            if not helper.status.Status().is_running(): break
            current_page = i + 1
            print(f"\nProcessing [{current_page}/{total_pages}]: {page_url}")
            if self.is_url_included_exclusion_list(page_url):
                self.move_url_from_page_urls_to_exclusion_urls(page_url)
                continue
            for attempt in range(max_retries):
                try:
                    # 1. ギャラリーページを開く
                    items = self.scraping(page_url, page_selectors)
                    languages = self.take_out(items, 'languages')
                    # ロボットチェック待機ロジック
                    if not languages or "Just a moment..." in driver.title:
                        print(f"  [!] ロボットチェック待機中... (10s)")
                        time.sleep(retry_delay)
                        items = Crawling.scraping_current(driver, page_selectors)
                        languages = self.take_out(items, 'languages')
                    title = Crawling.validate_title(items, 'title_jp', 'title_en')
                    url_title = helper.chromeDriver.ChromeDriver.fixed_file_name(page_url)
                    print(f"  タイトル: {title}, 言語: {languages}")
                    if languages == 'japanese':
                        # ダウンロードするときだけ通知する
                        # _line_message_api = LineMessageAPI(access_token="", channel_secret="")
                        # _line_message_api.send_message(
                        #     notification_id,
                        #     f'crawling :現在{current_page}ページ目 / 全{total_pages}ページ中 (残り{remaining_pages}ページ)')
                        _slack_message_api = helper.slack_message_api.SlackMessageAPI(access_token="")
                        _slack_message_api.send_message(
                            notification_id,
                            f'crawling :現在{current_page}ページ目 / 全{total_pages}ページ中 (残り{total_pages - current_page}ページ)')
                        image_items = self.scraping(page_url, image_selectors)
                        last_page_link = self.take_out(image_items, 'image_url')
                        if not last_page_link:
                            raise ValueError("最後のページへのリンク[{last_page_link}]が見つかりません")
                        print(f"  最終画像直リンク取得成功: {last_page_link}")
                        # --- ダウンロード処理 ---
                        # 直リンクを渡すので、web_file_list.pyが正しく連番を展開できるようになります
                        web_file_list = helper.webFileList.WebFileList([last_page_link])
                        web_file_list.update_value_object_by_deployment_url_list()
                        web_file_list.delete_local_folder()
                        web_file_list.download_irvine()
                        # 拡張子違いリトライ（既存ロジック）
                        for _ in helper.webFile.WebFile.ext_list:
                            if web_file_list.is_exist(): break
                            web_file_list.rename_url_ext_shift()
                            web_file_list.download_irvine()
                        # ZIP化・後処理
                        if web_file_list.make_zip_file():
                            web_file_list.rename_zip_file(title) or web_file_list.rename_zip_file(
                                f'{title}：{url_title}')
                            web_file_list.delete_local_files()
                            chrome_instance.save_source(
                                os.path.join(helper.webFileList.WebFileList.work_path, f'{title}：{url_title}.html'))
                            self.move_url_from_page_urls_to_exclusion_urls(page_url)
                            print("  処理成功。")
                        else:
                            web_file_list.delete_local_files()
                            self.move_url_from_page_urls_to_failure_urls(page_url)
                        break  # リトライループ終了
                    elif languages:
                        print(f"  対象外言語 ({languages})。除外リストへ。")
                        self.move_url_from_page_urls_to_exclusion_urls(page_url)
                        break
                    else:
                        raise ValueError("languages_empty")
                except Exception as e:
                    print(f"  エラー発生 (試行 {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        self.move_url_from_page_urls_to_failure_urls(page_url)

    def crawling_urls(self, page_selectors, image_selectors):
        """各ページをスクレイピングして、画像ファイルをダウンロード＆圧縮する
            # crawling_itemsに、page_urlsがあり、各page_urlをpage_selectorsでスクレイピングする
            # タイトルとURLでダウンロード除外または済みかをチェックして、
            # ダウンロードしない場合は、以降の処理をスキップする
            # 各page_urlをimage_selectorsでスクレイピングしてダウンロードする画像URLリストを作る。
            # 画像URLリストをirvineHelperでダウンロードして、zipファイルにする
        """
        crawling_items = self.get_crawling_items()
        page_urls = []
        if self.URLS_TARGET in crawling_items:
            page_urls = crawling_items[self.URLS_TARGET]
        for page_url in page_urls:
            status = helper.status.Status()
            if status is not None and not status.is_running():
                print("stop status")
                break
            print(page_url)
            if self.is_url_included_exclusion_list(page_url):
                self.move_url_from_page_urls_to_exclusion_urls(page_url)
                continue
            if self.is_url_included_failure_list(page_url):
                self.move_url_from_page_urls_to_failure_urls(page_url)
                continue
            items = self.scraping(page_url, page_selectors)
            title = Crawling.validate_title(items, 'title_jp', 'title_en')
            url_title = helper.chromeDriver.ChromeDriver.fixed_file_name(page_url)

            # フォルダがなかったらフォルダを作る
            os.makedirs(helper.webFileList.WebFileList.work_path, exist_ok=True)
            target_file_name = os.path.join(helper.webFileList.WebFileList.work_path, f'{title}：{url_title}.html')
            print(title)
            if not os.path.exists(target_file_name):
                image_items = self.scraping(page_url, image_selectors)
                image_urls = self.take_out(image_items, 'image_urls')
                print(image_urls)
                web_file_list = helper.webFileList.WebFileList(image_urls)
                web_file_list.download_irvine()
                for count in enumerate(helper.webFile.WebFile.ext_list):
                    if web_file_list.is_exist():
                        break
                    # ダウンロードに失敗しているときは、失敗しているファイルの拡張子を変えてダウンロードしなおす
                    web_file_list.rename_url_ext_shift()
                    web_file_list.download_irvine()
                if not web_file_list.make_zip_file():
                    sys.exit()
                if not web_file_list.rename_zip_file(title):
                    if not web_file_list.rename_zip_file(f'{title}：{url_title}'):
                        sys.exit()
                web_file_list.delete_local_files()
                # 成功したらチェック用ファイルを残す
                helper.chromeDriver.ChromeDriver().save_source(target_file_name)
            # page_urlsからexclusion_urlsにURLを移して保存する
            self.move_url_from_page_urls_to_exclusion_urls(page_url)
