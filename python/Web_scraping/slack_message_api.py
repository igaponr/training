import json
from dataclasses import dataclass, asdict
import os
from typing import Optional
from argparse import ArgumentParser
from slack_sdk import WebClient  # pip install slack_sdk
from slack_sdk.errors import SlackApiError


@dataclass(frozen=True)
class SlackMessageAPI:
    """
    Slack API のトークンを保持し、メッセージ送信機能と、
    設定情報のJSONファイル保存・ロード機能を提供するクラス。
    設定情報指定せずにインスタンス作成時は、JSONファイルがあればロードし、
    JSONファイルがなければエラー表示で終了します。
    """
    access_token: str
    json_path: str = "slack_message_api_config.json"
    client: WebClient = None

    def __post_init__(self):
        """
        トークンが指定されていない場合、JSONファイルからロードを試みる。
        JSONファイルが存在しない場合は、エラーメッセージを表示して終了する。
        """
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
        """
        指定したチャンネルにメッセージを送信する。

        Args:
            _channel_id: 送信先のチャンネルID。
            _message: 送信するメッセージ。
        Returns:
            送信に成功した場合はTrue、失敗した場合はFalseを返す。
        """

        try:
            self.client.chat_postMessage(channel=_channel_id, text=_message)
            return True
        except SlackApiError as e:
            print(f"メッセージの送信に失敗しました: {e}")
            return False

    def save_to_json(self) -> None:
        """
        設定情報をJSONファイルに保存する。
        """
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self), f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"設定情報の保存に失敗しました: {e}")

    @classmethod
    def load_from_json(cls, json_path: Optional[str] = None) -> "SlackMessageAPI":
        """
        JSONファイルから設定情報を読み込み、インスタンスを生成する。

        Args:
            json_path: JSONファイルのパス。指定しない場合は、デフォルトのパスを使用する。

        Returns:
            SlackMessageAPI インスタンス。
        """
        path = json_path or cls.json_path
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return cls(**data)
        else:
            raise FileNotFoundError(f"JSONファイルが見つかりません: {path}")


def get_option():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-a', '--access_token', type=str, default="",
                            help='Slack Notifyのアクセストークンを指定する')
    arg_parser.add_argument('-c', '--channel_id', type=str, default="#general",
                            help='Slack Notifayを送るチャンネルのIDを指定する')
    arg_parser.add_argument('-i', '--channel_id', type=str, default="#General",
                            help='メッセージを送るUserIDを指定する')
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
