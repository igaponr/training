# -*- coding: utf-8 -*-
import pytest
import os
import sys
import json
import pathlib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import helper.status


# テストデータ
@pytest.fixture(params=[
    ("running", helper.status.StatusValue.RUNNING),
    ("stop", helper.status.StatusValue.STOP),
    ("pending", helper.status.StatusValue.PENDING),
    ("error", helper.status.StatusValue.ERROR),
    ("unknown", helper.status.StatusValue.PENDING),  # 存在しないステータス値はPENDINGになる
])
def status_data(request, tmp_path):
    status_value, expected_status = request.param
    json_path = tmp_path / "status.json"
    with open(json_path, "w") as f:
        json.dump({"status": status_value}, f)
    return json_path, expected_status


# StatusValueのis_terminal()メソッドのテスト
def test_status_value_is_terminal():
    assert helper.status.StatusValue.STOP.is_terminal() is True
    assert helper.status.StatusValue.ERROR.is_terminal() is True
    assert helper.status.StatusValue.RUNNING.is_terminal() is False
    assert helper.status.StatusValue.PENDING.is_terminal() is False


# Statusクラスのテスト
class TestStatus:
    def test_init(self, status_data):
        json_path, expected_status = status_data
        status = helper.status.Status(json_path=json_path)
        assert status._status == expected_status

    def test_init_file_not_found(self, tmp_path):
        json_path = tmp_path / "not_exist.json"
        status = helper.status.Status(json_path=json_path)
        assert status._status == helper.status.StatusValue.PENDING

    def test_init_invalid_json(self, tmp_path):
        json_path = tmp_path / "invalid.json"
        with open(json_path, "w") as f:
            f.write("invalid json")
        with pytest.raises(ValueError):
            helper.status.Status(json_path=json_path)

    def test_is_running(self):
        status = helper.status.Status(json_path=pathlib.Path("./json/status.json"),_status=helper.status.StatusValue.RUNNING)
        assert status.is_running() is True
        status = helper.status.Status(json_path=pathlib.Path("./json/status.json"),_status=helper.status.StatusValue.STOP)
        assert status.is_running() is False

    def test_is_stop(self):
        status = helper.status.Status(json_path=pathlib.Path("./json/status.json"),_status=helper.status.StatusValue.STOP)
        assert status.is_stop() is True
        status = helper.status.Status(json_path=pathlib.Path("./json/status.json"),_status=helper.status.StatusValue.RUNNING)
        assert status.is_stop() is False
        status = helper.status.Status(json_path=pathlib.Path("./json/status.json"),_status=helper.status.StatusValue.ERROR)
        assert status.is_stop() is False

    def test_str(self):
        status = helper.status.Status(json_path=pathlib.Path("./json/status.json"),_status=helper.status.StatusValue.RUNNING)
        assert str(status) == "running"

    def test_save_to_json(self, tmp_path):
        json_path = tmp_path / "status.json"
        status = helper.status.Status(json_path=json_path, _status=helper.status.StatusValue.RUNNING)
        status.save_to_json()
        with open(json_path, "r") as f:
            data = json.load(f)
        assert data[helper.status.Status.KEY_NAME] == "running"

    def test_save_to_json_os_error(self, tmp_path, monkeypatch):
        # 一時ファイルを作成
        temp_file = tmp_path / "status.json"
        temp_file.touch()
        # ファイルを開いて書き込み権限を削除
        with open(temp_file, "w") as f:
            pass  # ファイルを開くだけで何も書き込まない
            # Windows で書き込み権限を削除
        import os
        os.chmod(temp_file, 0o444)
        status = helper.status.Status(json_path=temp_file, _status=helper.status.StatusValue.RUNNING)
        with pytest.raises(OSError):
            status.save_to_json()
        # テスト後に書き込み権限を戻す(クリーンアップ)
        os.chmod(temp_file, 0o644)
