#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""slackにメッセージを送る
"""
import json
from dataclasses import dataclass, asdict
import os
from typing import Optional
from argparse import ArgumentParser
from slack_sdk import WebClient  # pip install slack_sdk
from slack_sdk.errors import SlackApiError


@dataclass(frozen=True)
class SlackMessageAPI:
    """Slackの設定情報を管理して、メッセージを送信するクラス。
    access_tokenを指定せず、jsonファイルからaccess_tokenが読み込めない場合はアプリ終了する

    Args:
        access_token (str): (省略可)Slack API のトークンを指定する。指定しない場合はJSONファイルから読み込む
        json_path (str): (省略可)設定情報を保存するjsonファイルのパス
        client (WebClient): (省略可)Slack Clientのインスタンス
    Returns:
        SlackMessageAPI: インスタンス
    """
    access_token: str
    json_path: str = (os.path.dirname(__file__) + r"\..\json\slack_message_api_config.json")
    client: WebClient = None

    def __post_init__(self):
        if not self.access_token:
            try:
                loaded_self = self.load_from_json()
                object.__setattr__(self, "access_token", loaded_self.access_token)
            except FileNotFoundError:
                print(f"エラー: JSONファイル({self.json_path})が見つかりません。"
                      "トークンを指定するか、JSONファイルを作成してください。")
                exit(1)
        self.save_to_json()
        object.__setattr__(self, "client", WebClient(token=self.access_token))

    def send_message(self, _channel_id: str, _message: str) -> bool:
        """Slackにメッセージを送信する

        Args:
            _channel_id (str): 送信先のチャンネルID
            _message (str): 送信するメッセージ
        Returns:
            bool: 送信に成功した場合はTrue、失敗した場合はFalseを返す
        """

        try:
            self.client.chat_postMessage(channel=_channel_id, text=_message)
            return True
        except SlackApiError as e:
            print(f"メッセージの送信に失敗しました: {e}")
            return False

    def save_to_json(self) -> None:
        """設定情報をJSONファイルに保存する。
        設定情報の保存に失敗した場合は、エラーを表示して処理を継続する
        """
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self), f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"設定情報の保存に失敗しました: {e}")

    @classmethod
    def load_from_json(cls, json_path: Optional[str] = None) -> "SlackMessageAPI":
        """JSONファイルから設定情報を読み込み、インスタンスを生成する

        Args:
            json_path (str): (省略可)JSONファイルのパス。指定しない場合は、デフォルトのパスを使用する
        Returns:
            SlackMessageAPI: インスタンス
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
                            help='Slack Appsのアクセストークンを指定する')
    arg_parser.add_argument('-c', '--channel_id', type=str, default="#general",
                            help='メッセージを送るSlackチャンネルのIDを指定する')
    arg_parser.add_argument('-m', '--message', type=str, default="Hello from SlackMessageAPI!",
                            help='送るメッセージを指定する')
    return arg_parser.parse_args()


if __name__ == "__main__":
    arg = get_option()
    print(arg)
    if arg.access_token:
        slack = SlackMessageAPI(access_token=arg.access_token)
    else:
        slack = SlackMessageAPI(access_token="")
    if slack.send_message(arg.channel_id, arg.message):
        print("メッセージを送信しました。")
    else:
        print("メッセージの送信に失敗しました。")
