#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Irvineのヘルパー

- 説明
    - Irvineを使ってurlリストのファイルをダウンロードする　https://qiita.com/igapon1/items/4d92950259083ae6ba41
        - urlリストを渡してIrvineHelperインスタンスを作る。urlリストはIrvineHelperのlist_pathのファイルに保存される
            - 既にurlリストがファイルになっていれば、そのファイルパスを渡してIrvineHelperインスタンスを作る
        - downloadメソッドを呼ぶ。list_pathのファイルを引数に、irvineを起動する
            - あらかじめIrvineの設定を行っておくこと

- list_pathのファイルフォーマット
    - タブ区切りフォーマット
        - URL
        - 保存フォルダ
        - 別名で保存
        - 以降不明(17フィールド)

- Irvineの設定
    - キューフォルダにフォーカスを当ててIrvineを終了しておく。Irvine起動時にフォーカスの当たっているキューフォルダにurlリストが追加される
    - ダウンロードが終わったらIrvineを終了する
        - [オプション設定]-[イベント]-[OnDeactivateQueue]に新規作成で以下のスクリプトを書き込む
        - [全て終了時にIrvineを終了]をチェックする

- Irvineに設定するスクリプト

doneclose.dms:
```
/*
スクリプト初期化データ
guid={3FD7CA4D-BB58-4E4E-B1EF-E66AA72E9685}
caption=全て終了時にIrvineを終了
version=0
hint=
event=OnDeactivateQueue
match=
author=
synchronize=0
*/
function OnDeactivateQueue(irvine){
//すべてのダウンロード終了イベント
irvine.ExecuteAction('actFileClose');
}
```

# 参考

- [Irvine公式](http://hp.vector.co.jp/authors/VA024591/)
- [Irvineマニュアル](http://hp.vector.co.jp/authors/VA024591/doc/manual.html)
- [IrvineまとめWiki](https://w.atwiki.jp/irvinewiki/)
- [Irvineの設定](https://w.atwiki.jp/irvinewiki/pages/32.html)
- [Irvine Uploader](https://u1.getuploader.com/irvn/)
- [Irvine Part36スレ](https://mevius.5ch.net/test/read.cgi/win/1545612410)
"""
import sys
import os
import subprocess
from itertools import zip_longest
from dataclasses import dataclass, field
from typing import List, Optional, Union
# 最大再起回数を1万回にする
sys.setrecursionlimit(10000)


@dataclass(frozen=True)
class IrvineValue:
    """Irvineの値オブジェクトクラス

    Args:
        url_list (list): URLのリスト
        exe_path (str): (省略可)Irvine.exeのパス
        list_path (str): (省略可)Irvineでダウンロードするファイルリストのファイルパス
    Returns:
        IrvineValue: インスタンス
    Raises:
        ValueError: exe_pathとlist_pathのパスが存在しなければ例外を出す
    """
    url_list: List[str]
    exe_path: str = field(default=r'c:\Program1\irvine1_3_0\irvine.exe'.replace(os.sep, '/'))
    list_path: str = field(default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                '../irvine_download_list.txt').replace(os.sep, '/'))

    def __post_init__(self):
        """初期化後の処理

        Irvineの実行ファイルの存在確認を行う

        Raises:
            FileNotFoundError: Irvineの実行ファイルが存在しない場合
        """
        if not os.path.isfile(self.exe_path):
            raise FileNotFoundError(f"Irvine executable not found: {self.exe_path}")


@dataclass
class Irvine:
    """Irvineのヘルパー

    Args:
        value_object (IrvineValue or list or str):
         IrvineHelperValueは値オブジェクト、listはIrvineでダウンロードするURLリスト、strはIrvineでダウンロードするURL
        download_path (str): (省略可)ダウンロードするフォルダパス
        download_file_name_list (list): (省略可)保存するファイル名リスト
    Returns:
        value_object
    Raises:
        ValueError: value_objectが指定されないか、exe_pathとlist_pathのパスが存在しなければ、例外を出す
    """
    value_object: Optional[Union[IrvineValue, List[str], str]] = None
    download_path: Optional[str] = None
    download_file_name_list: List[str] = field(default_factory=lambda: [''])

    def __post_init__(self):
        """初期化後の処理

        `value_object` でバリューオブジェクトを指定するか、URLのリストか、URLを指定する
        ダウンロードリストファイルの存在確認を行う

        Raises:
            ValueError: `value_object` と `url_list` の両方が指定されていない場合
            FileNotFoundError: `value_object` で指定されたダウンロードリストファイルが存在しない場合
        """
        if not self.value_object:
            raise ValueError("Either value_object or url_list must be provided.")
        if isinstance(self.value_object, str):
            self.value_object = [self.value_object]
        if isinstance(self.value_object, List):
            self.value_object = IrvineValue(url_list=self.value_object)
        if not isinstance(self.value_object, IrvineValue):
            raise ValueError("Either value_object or url_list must be provided.")
        self.create_download_file()
        if not os.path.isfile(self.value_object.list_path):
            raise FileNotFoundError(f"Download list file not found: {self.value_object.list_path}")

    def create_download_file(self) -> None:
      """ダウンロードリストファイルを作成する

      `url_list`、`download_path`、`download_file_name_list` をもとに、Irvineのダウンロードリストファイルを作成する
      ファイルフォーマットは、URL、保存フォルダ、別名で保存、タブ区切り（17フィールド）となる

      Raises:
          OSError: ファイルの作成に失敗した場合
          Exception: その他のエラーが発生した場合
      """
      try:
          with open(self.value_object.list_path, 'w', encoding='utf-8') as work_file:
              for url, file_name in zip_longest(self.value_object.url_list, self.download_file_name_list):
                  line = f"{url}\t{self.download_path or ''}\t{file_name or ''}\t" + "\t" * 17 + "\n"
                  work_file.write(line)
      except IOError as e:
          raise IOError(f"Failed to create download list file: {e}") from e

    def download(self) -> None:
        """Irvineを実行してファイルダウンロードを行う

        Irvineを実行し、ダウンロードリストファイルに基づいてファイルのダウンロードを行う
        Irvineの実行が完了するまで待機する

        Raises:
            RuntimeError: Irvineの実行に失敗した場合、またはその他のエラーが発生した場合
        """
        cmd = f"{self.value_object.exe_path} {self.value_object.list_path}"
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            if proc.returncode != 0:
                error_message = (f"Irvine execution failed with code {proc.returncode}.\n"
                                 f"Stdout: {stdout.decode()}\nStderr: {stderr.decode()}")
                raise RuntimeError(error_message)
        except Exception as e:
            raise RuntimeError(f"Failed to download files: {e}") from e
