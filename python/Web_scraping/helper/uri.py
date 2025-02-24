#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""URIを扱うためのヘルパークラスを提供します

- このモジュールは、URI文字列を検証し、Data URIに関する情報を取得するための機能を提供します
- Uriクラスは、URI文字列またはUriValueオブジェクトからインスタンス化できます
- Data URIのMIMEタイプ、データ、ファイル名、拡張子などを取得するメソッドが提供されています
- 参考
    - https://pypi.org/project/python-datauri/
    - https://github.com/fcurella/python-datauri/tree/py3
    - https://qiita.com/TsubasaSato/items/908d4f5c241091ecbf9b

Examples:
    >>> uri_helper = Uri("https://www.example.com/image.jpg")
    >>> print(uri_helper.get_filename())
    image
    >>> print(uri_helper.get_ext())
    .jpg

    >>> data_uri = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
    >>> uri_helper = Uri(data_uri)
    >>> print(uri_helper.is_jpeg_data_uri())
    True
    >>> uri_helper.save_data_uri("image.jpg")
"""
import copy
from urllib.parse import *  # URLパーサー
from dataclasses import dataclass
from datauri import DataURI, InvalidDataURI


@dataclass(frozen=True)
class UriValue:
    """URI文字列を保持する値オブジェクト

    Attributes:
        uri: URI文字列
    """
    uri: str

    def __post_init__(self):
        """インスタンス作成後のバリデーションを行います"""
        if not self.uri:
            raise ValueError("uriは必須です。")
        if not self.is_uri_only(self.uri):
            raise ValueError(f"無効なURIです: {self.uri}")

    @staticmethod
    def is_uri_only(string: str) -> bool:
        """文字列がURIのみで構成されているかどうかを判定します

        Args:
            string: 判定対象の文字列

        Returns:
            URIのみで構成されている場合はTrue、そうでない場合はFalse
        """
        return len(urlparse(string).scheme) > 0


class Uri:
    """URIを扱うためのヘルパークラス。"""
    def __init__(self, value_object: UriValue | str):
        """Uriオブジェクトを初期化します

        Args:
            value_object: URI文字列またはUriValueオブジェクト

        Raises:
            ValueError: value_objectが無効な値の場合
        """
        if isinstance(value_object, UriValue):
            self.value_object = copy.deepcopy(value_object)
        elif isinstance(value_object, str):
            self.value_object = UriValue(value_object)
        else:
            raise ValueError(f"value_objectはUriValueまたはstrでなければなりません: {type(value_object)}")

    @staticmethod
    def is_data_uri(url: str) -> bool:
        """指定されたURLがData URIかどうかを判定します

        Args:
            url: 判定対象のURL

        Returns:
            Data URIの場合はTrue、そうでない場合はFalse
        """
        try:
            DataURI(url)
            return True
        except InvalidDataURI:
            return False

    @staticmethod
    def is_jpeg_data_uri(url: str) -> bool:
        """指定されたURLがJPEG形式のData URIかどうかを判定します

        Args:
            url: 判定対象のURL

        Returns:
            JPEG形式のData URIの場合はTrue、そうでない場合はFalse
        """
        try:
            return urlparse(url).scheme == 'data' and DataURI(url).mimetype == 'image/jpeg' and DataURI(url).is_base64
        except:
            return False

    @staticmethod
    def is_png_data_uri(url: str) -> bool:
        """指定されたURLがPNG形式のData URIかどうかを判定します

        Args:
            url: 判定対象のURL

        Returns:
            PNG形式のData URIの場合はTrue、そうでない場合はFalse
        """
        try:
            return urlparse(url).scheme == 'data' and DataURI(url).mimetype == 'image/png' and DataURI(url).is_base64
        except:
            return False

    def get_uri(self) -> str:
        """URIを取得します

        Returns:
            URI文字列
        """
        return copy.deepcopy(self.value_object.uri)

    def get_data_uri(self) -> DataURI:
        """DataURIオブジェクトを取得します

        Returns:
            DataURIオブジェクト
        """
        return DataURI(self.get_uri())

    def get_data(self) -> bytes:
        """Data URIのデータを取得します

        Returns:
            Data URIのデータ（バイト列）
        """
        return self.get_data_uri().data

    def save_data_uri(self, target_file: str):
        """Data URIのデータをファイルに保存します

        Args:
            target_file: 保存先のファイルパス
        """
        with open(target_file, "wb") as image_file:
            image_file.write(self.get_data())

    def is_enable_filename(self) -> bool:
        """ファイル名を取得できるかどうかを判定します

        Returns:
            ファイル名を取得できる場合はTrue、そうでない場合はFalse
        """
        if self.is_data_uri(self.get_uri()):
            return self.get_data_uri().name is not None
        else:
            parsed_url = urlparse(self.get_uri())
            return bool(parsed_url.path) and not parsed_url.path.endswith("/")

    def get_filename(self) -> str | None:
        """ファイル名を取得します

        拡張子は含まれません。Data URIの場合は、filenameパラメータから取得します
        ファイル名が存在しない場合はNoneを返します

        Returns:
            ファイル名（拡張子なし）
        """
        if self.is_data_uri(self.get_uri()):
            uri = self.get_uri()
            # filenameパラメータが存在する場合
            if 'filename=' in uri:
                filename = uri.split('filename=')[1]
                # 最初の ; か , までをファイル名として抽出
                if ';' in filename:
                    filename = filename.split(';', 1)[0]
                if ',' in filename :
                    filename = filename.split(',', 1)[0]
                return filename
            else:
              return self.get_data_uri().name #filenameがない場合は、従来のロジックを使用
        else:
            parsed_url = urlparse(self.get_uri())
            path = parsed_url.path
            if not path or path.endswith("/"):
                return None
            filename = path.split("/")[-1]
            if '=' in filename:
                filename = filename.split('=', 1)[1] #修正
            if ';' in filename:
                filename = filename.split(';', 1)[0] #修正
            if "." in filename:
                return filename.rsplit(".", 1)[0]
            else:
                return filename

    def get_ext(self) -> str | None:
        """拡張子を取得します

        ドット(.)を含みます。Data URIの場合は、DataURIオブジェクトのextension属性を参照します
          拡張子が存在しない場合はNoneを返します

        Returns:
           拡張子（ドットを含む）
        """
        if self.is_data_uri(self.get_uri()):
            data_uri = self.get_data_uri()
            try:
                return data_uri.extension
            except AttributeError: # extension属性がない場合の処理
                mimetype = data_uri.mimetype
                if mimetype == "image/jpeg":
                    return ".jpg"
                elif mimetype == "image/png":
                    return ".png"
                # 他のmimetypeにも対応する場合、ここに追加する
                else:
                    return None
        else:
            parsed_url = urlparse(self.get_uri())
            path = parsed_url.path
            if not path or path.endswith("/") or "." not in path :
                return None
            else:
              return "." + path.rsplit(".", 1)[1]
