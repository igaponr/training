#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Irvineのヘルパー

- 記事[Irvineを使ってurlリストのファイルをダウンロードする](https://qiita.com/igapon1/items/4d92950259083ae6ba41)で紹介した
- 事前にIrvineの設定を行っておく必要がある
- urlやurlリストから、IrvineValueインスタンスを作る
- IrvineValueインスタンスから、list_pathにIrvineのダウンロードファイルを作る
    - Irvineのダウンロードファイルのフォーマット(タブ区切りcsv)
        - URL
        - 保存フォルダ
        - 別名で保存
        - 以降不明(17フィールド)
- downloadメソッドでIrvineを使ってList_pathのファイルをダウンロードする
    - 以下のIrvineの設定を行っておくこと
        - キューフォルダにフォーカスを当ててIrvineを終了しておく。Irvine起動時にフォーカスの当たっているキューフォルダにurlリストが追加される
        - ダウンロードが終わったらIrvineを終了する
            - [オプション設定]-[イベント]-[OnDeactivateQueue]に新規作成で後述のスクリプトを書き込む
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
- 参考
    - [Irvine公式](http://hp.vector.co.jp/authors/VA024591/)
    - [Irvineマニュアル](http://hp.vector.co.jp/authors/VA024591/doc/manual.html)
    - [IrvineまとめWiki](https://w.atwiki.jp/irvinewiki/)
    - [Irvineの設定](https://w.atwiki.jp/irvinewiki/pages/32.html)
    - [Irvine Uploader](https://u1.getuploader.com/irvn/)
    - [Irvine Part36スレ](https://mevius.5ch.net/test/read.cgi/win/1545612410)

Example:
    >>> urls = ["http://example.com/file1.txt", "http://example.com/file2.txt"]
    >>> irvine = Irvine(urls, download_path="C:/downloads", download_file_name_list=["file1_renamed.txt", "file2_renamed.txt"])
    >>> irvine.download()
"""
import os
import subprocess
from itertools import zip_longest
from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass(frozen=True)
class IrvineValue:
    """Irvineの値オブジェクトクラス

    Args:
        url_list (list): ダウンロードするURLのリスト
        exe_path (str): Irvine.exeのパス。デフォルトは "c:\Program1\irvine1_3_0\irvine.exe"
        list_path (str): Irvineでダウンロードするファイルリストのファイルパス。デフォルトは "../irvine_download_list.txt"

    Raises:
        FileNotFoundError: exe_pathで指定されたファイルが存在しない場合
    """
    url_list: List[str]
    exe_path: str = field(default=r'c:\Program1\irvine1_3_0\irvine.exe'.replace(os.sep, '/'))
    list_path: str = field(default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                '../irvine_download_list.txt').replace(os.sep, '/'))

    def __post_init__(self):
        """初期化後の処理

        Irvine実行ファイルの存在を確認する

        Raises:
            FileNotFoundError: Irvineの実行ファイルが存在しない場合
        """
        if not os.path.isfile(self.exe_path):
            raise FileNotFoundError(f"Irvine executable not found: {self.exe_path}")


@dataclass
class Irvine:
    """Irvineのヘルパー

    Attributes:
        value_object (Optional[Union[IrvineValue, List[str], str]]): IrvineValueオブジェクト、URLリスト、またはURL文字列。
        download_path (Optional[str]): ダウンロード先のフォルダパス。指定しない場合は、Irvineのデフォルト設定が使用される。
        download_file_name_list (List[str]): ダウンロードするファイルのファイル名リスト。指定しない場合は、元のファイル名が使用される。

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
        ダウンロードリストファイルの存在を確認する

        Raises:
            ValueError: `value_object`が指定されていない場合
            FileNotFoundError: ダウンロードリストファイルが存在しない場合
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
      """Irvine用のダウンロードリストファイルを作成する

      ファイルフォーマットは、URL、保存フォルダ、別名で保存、タブ区切り（17フィールド）となる

      Raises:
          OSError: ファイルの作成に失敗した場合
      """
      try:
          with open(self.value_object.list_path, 'w', encoding='utf-8') as work_file:
              for url, file_name in zip_longest(self.value_object.url_list, self.download_file_name_list):
                  line = f"{url}\t{self.download_path or ''}\t{file_name or ''}\t" + "\t" * 17 + "\n"
                  work_file.write(line)
      except IOError as e:
          raise IOError(f"Failed to create download list file: {e}") from e

    def download(self) -> None:
        """Irvineを実行してダウンロードを行う

        Irvineを実行し、ダウンロードリストファイルに基づいてファイルのダウンロードを行い、Irvineの実行が完了するまで待機する

        Raises:
            RuntimeError: Irvineの実行に失敗した場合
        """
        cmd = [self.value_object.exe_path, self.value_object.list_path]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Irvine execution failed with code {e.returncode}.\n"
                             f"Stdout: {e.stdout}\nStderr: {e.stderr}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to download files: {e}") from e
