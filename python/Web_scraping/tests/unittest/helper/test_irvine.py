import pytest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import helper.irvine
import helper.webFileListHelper

# テストデータ
TEST_URLS = ["https://www.example.com/test1.txt", "https://www.example.com/test2.txt"]
TEST_FILE_NAMES = ["test1.txt", "test2.txt"]
TEST_DOWNLOAD_PATH = "test_downloads"


@pytest.fixture
def temp_download_list_file(tmp_path):
    """一時的なダウンロードリストファイルを作成するfixture."""
    list_file = [tmp_path / "download_list1.txt",
                 tmp_path / "download_list2.txt",
                 ]
    return list_file


@pytest.fixture
def irvine_value(monkeypatch, tmp_path, temp_download_list_file):
    """IrvineHelperValueのインスタンスを作成するfixture."""
    # Irvine.exeのパスはダミーを使用（実際には存在しないパス）
    dummy_exe_path = str(tmp_path / "dummy_irvine.exe")
    monkeypatch.setattr(helper.irvine.IrvineValue, "exe_path", dummy_exe_path)
    return helper.irvine.IrvineValue(temp_download_list_file)


# テストケース

def test_create_download_file(irvine_value, temp_download_list_file):
    """ダウンロードリストファイルが正しく作成されることをテストする"""
    # IrvineHelperValueのlist_pathを一時ファイルに設定した新しいインスタンスを作成
    new_irvine_value = helper.irvine.IrvineValue(url_list=TEST_URLS,
                                                 exe_path=irvine_value.exe_path,
                                                 list_path=irvine_value.list_path)
    irvine = helper.irvine.Irvine(
        value_object=new_irvine_value,
        download_path=TEST_DOWNLOAD_PATH,
        download_file_name_list=TEST_FILE_NAMES,
    )
    irvine.create_download_file()
    with open(irvine_value.list_path, "r", encoding="utf-8") as work_file:
        lines = work_file.readlines()
    assert len(lines) == 2
    assert lines[0] == f"{TEST_URLS[0]}\t{TEST_DOWNLOAD_PATH}\t{TEST_FILE_NAMES[0]}\t" + "\t" * 17 + "\n"
    assert lines[1] == f"{TEST_URLS[1]}\t{TEST_DOWNLOAD_PATH}\t{TEST_FILE_NAMES[1]}\t" + "\t" * 17 + "\n"


def test_download_raises_error_when_exe_not_found(irvine_value, temp_download_list_file):
    """Irvine.exeが存在しない場合にエラーが発生することをテストする"""
    with pytest.raises(FileNotFoundError):
        helper.irvine.IrvineValue(url_list=TEST_URLS,
                                  exe_path=r"c:\windows\temp\irvine.exe",
                                  list_path=irvine_value.list_path)

def test_init_with_value_object(irvine_value, temp_download_list_file):
    """value_objectで初期化できることをテストする"""
    with open(irvine_value.list_path, 'w', encoding='utf-8') as work_file:
        work_file.write('')
    new_irvine_value = helper.irvine.IrvineValue(url_list=irvine_value.url_list,
                                                 exe_path=irvine_value.exe_path,
                                                 list_path=irvine_value.list_path)
    irvine = helper.irvine.Irvine(
        value_object=new_irvine_value,
        download_path=TEST_DOWNLOAD_PATH,
        download_file_name_list=TEST_FILE_NAMES,
    )
    assert irvine.value_object == irvine_value
    with open(irvine_value.list_path, "r", encoding="utf-8") as work_file:
        lines = work_file.readlines()
    assert len(lines) == 2
    assert lines[0] == f"{temp_download_list_file[0]}\t{TEST_DOWNLOAD_PATH}\t{TEST_FILE_NAMES[0]}\t" + "\t" * 17 + "\n"
    assert lines[1] == f"{temp_download_list_file[1]}\t{TEST_DOWNLOAD_PATH}\t{TEST_FILE_NAMES[1]}\t" + "\t" * 17 + "\n"

def test_init_with_url_list(irvine_value, temp_download_list_file):
    """url_listで初期化できることをテストする"""
    irvine = helper.irvine.Irvine(value_object=TEST_URLS)
    assert irvine.value_object is not None
    assert os.path.isfile(irvine.value_object.list_path)
    with open(irvine_value.list_path, "r", encoding="utf-8") as work_file:
        lines = work_file.readlines()
    assert len(lines) == 2
    assert lines[0] == f"{TEST_URLS[0]}\t\t\t" + "\t" * 17 + "\n"
    assert lines[1] == f"{TEST_URLS[1]}\t\t\t" + "\t" * 17 + "\n"

def test_init_with_url_str(irvine_value, temp_download_list_file):
    """url_listで初期化できることをテストする"""
    irvine = helper.irvine.Irvine(value_object=TEST_URLS[0])
    assert irvine.value_object is not None
    assert os.path.isfile(irvine.value_object.list_path)
    with open(irvine_value.list_path, "r", encoding="utf-8") as work_file:
        lines = work_file.readlines()
    assert len(lines) == 1
    assert lines[0] == f"{TEST_URLS[0]}\t\t\t" + "\t" * 17 + "\n"

def test_init_raises_error_when_no_value_object_or_url_list():
    """value_objectとurl_listが指定されていない場合にエラーが発生することをテストする"""
    with pytest.raises(ValueError):
        helper.irvine.Irvine()

def test_init_raises_error_when_list_path_not_found(monkeypatch, tmp_path):
    """ダウンロードリストファイルが存在しない場合にエラーが発生することをテストする"""
    # 存在しないパスを指定
    dummy_exe_path = str(tmp_path / "dummy_irvine.exe")
    with pytest.raises(FileNotFoundError):
        helper.irvine.IrvineValue(url_list=TEST_URLS, exe_path=dummy_exe_path, list_path="not_existing_path.txt")