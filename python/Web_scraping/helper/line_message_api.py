#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LINEにメッセージを送る
"""
import json
from dataclasses import dataclass, asdict
import os
from typing import Optional
from argparse import ArgumentParser
from linebot import LineBotApi, WebhookHandler  # pip install line-bot-sdk
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import TextSendMessage
# 警告抑制
import warnings
from linebot import LineBotSdkDeprecatedIn30


@dataclass(frozen=True)
class LineMessageAPI:
    """LINEの設定情報を管理して、メッセージを送信するクラス。
    access_tokenとchannel_secretを指定せず、jsonファイルからaccess_tokenとchannel_secretが読み込めない場合はアプリ終了する

    Args:
        access_token (str): (省略可)LINE Messaging API のトークンを指定する。指定しない場合はJSONファイルから読み込む
        channel_secret (str): (省略可)Channel Secretを指定する。指定しない場合はJSONファイルから読み込む
        json_path (str): (省略可)設定情報を保存するjsonファイルのパス
        line_bot_api (LineBotApi): (省略可)LineBotApiインスタンス
        handler (WebhookHandler): (省略可)WebhookHandlerインスタンス
    Returns:
        LineMessageAPI: インスタンス
    """
    access_token: str
    channel_secret: str
    json_path: str = (os.path.dirname(__file__) + r"\..\json\line_message_api_config.json")
    line_bot_api: LineBotApi = None  # 型ヒントを追加
    handler: WebhookHandler = None  # 型ヒントを追加

    def __post_init__(self):
        if not self.access_token or not self.channel_secret:
            try:
                loaded_self = self.load_from_json()
                # _replace で frozen な dataclass の属性を更新
                object.__setattr__(self, "access_token", loaded_self.access_token)
                object.__setattr__(self, "channel_secret", loaded_self.channel_secret)
            except FileNotFoundError:
                print(f"エラー: JSONファイル({self.json_path})が見つかりません。"
                      "アクセストークンとChannel Secretを指定するか、JSONファイルを作成してください。")
                exit(1)
        self.save_to_json()
        object.__setattr__(self, "line_bot_api", LineBotApi(self.access_token))
        object.__setattr__(self, "handler", WebhookHandler(self.channel_secret))

    def send_message(self, user_id: str, message: str) -> bool:
        """Slackにメッセージを送信する

        Args:
            user_id (str): 送信先のユーザーID
            message (str): 送信するメッセージ
        Returns:
            bool: 送信に成功した場合はTrue、失敗した場合はFalseを返す
        """
        text_message = TextSendMessage(text=message)
        try:
            self.line_bot_api.push_message(user_id, text_message)
            return True  # 送信成功
        except LineBotApiError as e:
            print(f"メッセージの送信に失敗しました: {e}")
            return False  # 送信失敗

    def save_to_json(self) -> None:
        """設定情報をJSONファイルに保存する。
        設定情報の保存に失敗した場合は、エラーを表示して処理を継続する
        """
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self), f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"メッセージの保存に失敗しました: {e}")

    @classmethod
    def load_from_json(cls, json_path: Optional[str] = None) -> "LineMessageAPI":
        """JSONファイルから設定情報を読み込み、インスタンスを生成する

        Args:
            json_path (str): JSONファイルのパス。指定しない場合は、デフォルトのパスを使用する
        Returns:
            LineMessageAPI: インスタンス
        Raises:
            FileNotFoundError: JSONファイルが見つからない、設定情報の保存に失敗した
        """
        path = json_path or cls.json_path
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return cls(**data)
        else:
            raise FileNotFoundError(f"JSONファイルが見つかりません: {path}")


def get_option():
    """オプションをパースする

    Returns:
        Namespace: オプションのパース結果
    """
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-a', '--access_token', type=str, default="",
                            help='LINE Messege APIのアクセストークンを指定する')
    arg_parser.add_argument('-c', '--channel_secret', type=str, default="",
                            help='LINE Messege APIのチャンネルシークレットを指定する')
    arg_parser.add_argument('-i', '--user_id', type=str, default="",
                            help='メッセージを送るUserIDを指定する')
    arg_parser.add_argument('-m', '--message', type=str, default="Hello from Python!",
                            help='送るメッセージを指定する')
    return arg_parser.parse_args()


if __name__ == '__main__':  # インポート時には動かない
    # 警告抑制 v3 api
    warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)
    arg = get_option()
    print(arg)
    if arg.access_token:
        line_message_api = LineMessageAPI(access_token=arg.access_token, channel_secret=arg.channel_secret)
    else:
        line_message_api = LineMessageAPI(access_token="", channel_secret="")
    if line_message_api.send_message(arg.user_id, arg.message):
        print("メッセージを送信しました。")
    else:
        print("メッセージの送信に失敗しました。")
