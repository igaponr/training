#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""statusファイル

Todo:
    - docstringを整える
"""
import json
import time
from dataclasses import dataclass
import os
from typing import Callable, Protocol


class SupportsIsRunning(Protocol):
    def __call__(self) -> bool: ...


@dataclass(frozen=True)
class Status:
    """システムの状態を表すValue Object."""
    json_path: str = (os.path.dirname(__file__) + r"\..\json\status.json")
    _status: str = None

    def __post_init__(self):
        """インスタンス生成後に、ファイルからステータスを読み込むか、デフォルト値を設定する"""
        try:
            loaded_self = self.load_from_json()
            object.__setattr__(self, "_status", loaded_self)
        except FileNotFoundError:
            object.__setattr__(self, "_status", "pending")
        # ロード後、もしくはpending設定後にバリデーション
        self.validate(self._status)

    @staticmethod
    def validate(value):
        """有効なステータス値であることを確認する。"""
        valid_statuses = ["running", "stop", "pending", "error"]
        if value not in valid_statuses:
            raise ValueError(f"Invalid status value: {value}. Valid values are: {valid_statuses}")

    def is_running(self):
        return self._status == "running"

    def is_stop(self):
        return self._status == "stop"

    def __str__(self):
        return self._status

    def load_from_json(self):
        """status.jsonファイルからステータスを読み込む。"""
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"File not found: {self.json_path}")

        try:
            with open(self.json_path, 'r') as f:
                data = json.load(f)
                if 'status' not in data:
                    raise ValueError(f"'status' key not found in {self.json_path}")
                return data['status']
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in {self.json_path}")

    def save_to_json(self):
        """現在のステータスをstatus.jsonファイルに保存する。"""
        try:
            with open(self.json_path, 'w') as f:
                json.dump({"status": self._status}, f, indent=2)
        except Exception as e:
            raise IOError(f"Failed to save status to {self.json_path}: {e}")


if __name__ == "__main__":
    try:
        # 初期化。ファイルがあればロード、なければpending
        status = Status()
        print(f"Initial status: {status}")
    except ValueError as e:
        print(f"Error: {e}")
    except IOError as e:
        print(f"Error: {e}")
