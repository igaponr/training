#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""システムの状態を管理するための Status クラスを提供します

- Status クラスは、状態を表す値オブジェクトであり、現在の状態を status.json ファイルに保存し、読み込めます
- 状態は StatusValue 列挙型で定義され、RUNNING、STOP、PENDING、ERROR のいずれかの値を取ります
- Status クラスは、状態の確認、設定、ファイルへの保存、ファイルからの読み込みを行うためのメソッドを提供します
- さらに、終了状態かどうかを判断する is_terminal() メソッドを StatusValue に追加しました
- Status クラスの is_stop() メソッドは is_terminal() を利用するため、ステータス値の追加や変更に柔軟に対応できます
"""
import json
import pathlib
from dataclasses import dataclass, field
from enum import Enum


class StatusValue(Enum):
    """システムのステータス値を表す列挙型

    Attributes:
        RUNNING: 実行中
        STOP: 停止
        PENDING: 保留中
        ERROR: エラー
    """
    RUNNING = "running"
    STOP = "stop"
    PENDING = "pending"
    ERROR = "error"

    def is_terminal(self) -> bool:
        """ステータスが終了状態かどうかを返す

        Returns:
            True: 終了状態 (STOP または ERROR) の場合、False: それ以外の場合
        """
        return self in (StatusValue.STOP, StatusValue.ERROR)


@dataclass(frozen=True)
class Status:
    """システムの状態を表すValue Object

    status.jsonファイルからステータスを読み込み、保持する
    ファイルが存在しない場合は、デフォルトでPENDING状態となる

    Attributes:
        json_path: ステータスを保存するJSONファイルのパス
        _status: システムの現在のステータス

    Raises:
        ValueError: status.jsonファイルの形式が不正な場合
    """
    json_path: pathlib.Path = field(
        default_factory=lambda: pathlib.Path(__file__).parent.parent / "json" / "status.json",
        metadata={"help": "ステータスを保存するJSONファイルのパス  .. :noindex:"}
    )
    _status: StatusValue = field(default=StatusValue.PENDING)
    KEY_NAME: str = 'status'

    def __post_init__(self):
        """インスタンス初期化の処理。JSONファイルからステータスを読み込む"""
        if self.json_path.exists() and self.json_path.stat().st_size > 0:
            try:
                object.__setattr__(self, "_status", self._load_from_json())
            except FileNotFoundError:
                print(f"Status file not found: {self.json_path}. Using default 'pending' status.")
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid JSON format in {self.json_path}: {e}")

    def is_running(self) -> bool:
        """システムが実行中かどうかを返す

        Returns:
            True: 実行中の場合、False: それ以外の場合
        """
        return self._status == StatusValue.RUNNING

    def is_stop(self) -> bool:
        """システムが停止状態かどうかを返す

        Returns:
            True: 停止状態の場合、False: それ以外の場合
        """
        return self._status.is_terminal() and self._status == StatusValue.STOP

    def __str__(self) -> str:
        """ステータス値の文字列表現を返す

        Returns:
            ステータス値の文字列
        """
        return self._status.value

    def _load_from_json(self) -> StatusValue:
        """status.jsonファイルからステータスを読み込む

        jsonにKEY_NAMEが無ければ、PENDINGで読み込む
        KEY_NAMEの値がStatusValueの値でなければ、PENDINGで読み込む

        Returns:
            読み込んだステータス値

        Raises:
            ValueError: status.jsonファイルが不正なJSON形式の場合
        """
        try:
            with open(self.json_path, 'r') as f:
                data: dict = json.load(f)
                l_status = data.get(self.KEY_NAME, StatusValue.PENDING.value)
                if l_status not in StatusValue:
                    l_status = StatusValue.PENDING
                return StatusValue(l_status)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {self.json_path}: {e}")

    def save_to_json(self):
        """現在のステータスをstatus.jsonファイルに保存する

        Raises:
            OSError: ファイルの保存に失敗した場合
        """
        try:
            self.json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.json_path, 'w') as f:
                json.dump({self.KEY_NAME: self._status.value}, f, indent=2)
        except OSError as e:
            raise OSError(f"Failed to save status to {self.json_path}: {e}")
