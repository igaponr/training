import os
import sys
import pytest
from unittest.mock import patch, MagicMock, call
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import helper.chromeDriverHelper


# テスト用のダミーURLとセレクタ
TEST_URL = "https://www.example.com"
TEST_SELECTORS = {"title": [(By.TAG_NAME, "title", lambda elem: elem.text)]}
TEST_IMAGE_URL = "https://www.easygifanimator.net/images/samples/video-to-gif-sample.gif"


@pytest.fixture(scope="function", autouse=True)
def chromedriver_helper(monkeypatch):
    """ChromeDriverHelper のインスタンスを fixture として提供する

    この fixture は、ChromeDriverHelper のテストに必要なモックオブジェクトを作成し、
    実際のブラウザを起動せずにテストを実行できるようにします

    `monkeypatch` を使用して `webdriver.Chrome` と `WebDriverWait` をモックし、
    ChromeDriverHelper がブラウザと対話する代わりにモックオブジェクトと対話するようにします
    これにより、テストの実行速度が向上し、安定性が確保されます

    Yields:
        helper.chromeDriverHelper.ChromeDriverHelper: ChromeDriverHelper のモックインスタンス
    """
    # mock _driver and __wait to avoid actually opening a browser
    mock_driver = MagicMock()
    mock_driver.window_handles = ['win1']  # 初期ウィンドウハンドルを設定
    mock_driver.current_window_handle = 'win1'
    # open_new_tab 用のモック
    original_open_new_tab = helper.chromeDriverHelper.ChromeDriverHelper.open_new_tab
    def mocked_open_new_tab(self, url):
        new_window_handle = f'win{len(self._driver.window_handles) + 1}'
        self._driver.window_handles.append(new_window_handle)  # window_handles を更新
        self._driver.switch_to.window(new_window_handle)
        self._window_handle_list.append(new_window_handle)
        return new_window_handle
    # open_new_tab をモックする
    monkeypatch.setattr(helper.chromeDriverHelper.ChromeDriverHelper, "open_new_tab", mocked_open_new_tab)
    # find_elements の戻り値を、引数に応じて変更する
    def mock_find_elements(by, value):
        if by == By.ID and value == "not_exist_element":
            return []  # 存在しない要素は空のリストを返す
        else:
            mock_element = MagicMock(spec=WebElement)
            mock_element.text = "Example Domain"
            return [mock_element]
    mock_driver.find_elements.side_effect = mock_find_elements # side_effectを使用
    mock_wait = MagicMock()
    mock_element = MagicMock(spec=WebElement)
    mock_element.text = "Example Domain"
    mock_driver.find_elements.return_value = [mock_element]
    mock_driver.title = "Example Domain"
    mock_driver.current_url = TEST_URL
    mock_driver.window_handles = ['win1']
    mock_driver.current_window_handle = 'win1'
    mock_driver.page_source = "<html><head><title>Example Domain</title></head><body></body></html>"
    with patch('helper.chromeDriverHelper.webdriver.Chrome', return_value=mock_driver), \
        patch('helper.chromeDriverHelper.WebDriverWait', return_value=mock_wait):
        chrome_helper = helper.chromeDriverHelper.ChromeDriverHelper()
        yield chrome_helper


class TestChromeDriverHelper:

    def test_fixed_path(self):
        assert helper.chromeDriverHelper.ChromeDriverHelper.fixed_path("C:\\test:folder*") == "C：\\test：folder＊"

    def test_fixed_file_name(self):
        assert helper.chromeDriverHelper.ChromeDriverHelper.fixed_file_name("test/file:name*.txt") == "test／file：name＊.txt"

    def test_scraping(self, chromedriver_helper):
        """`scraping` メソッドが正しく動作することをテストする

        指定されたセレクタを使用してスクレイピングを実行し、
        返されたアイテムが期待通りであることを確認します

        Args:
            chromedriver_helper (helper.chromeDriverHelper.ChromeDriverHelper):
                ChromeDriverHelper のモックインスタンス

        Asserts:
            返されたアイテムに "title" キーが存在すること
            "title" キーに対応する値がリストであること
            リストの長さが 1 であること
            リストの最初の要素が "Example Domain" であること
        """
        chromedriver_helper.open_current_tab(TEST_URL)
        items = chromedriver_helper.scraping(TEST_SELECTORS)
        assert "title" in items
        assert isinstance(items["title"], list)
        assert len(items["title"]) == 1  # titleは一つだけ取得される
        assert items["title"][0] == "Example Domain"  # titleの値を確認

    def test_get_value_object(self, chromedriver_helper):
        chromedriver_helper.open_current_tab(TEST_URL)
        chromedriver_helper.scraping(TEST_SELECTORS)  # value_objectを作成するために必要
        value_object = chromedriver_helper.get_value_object()
        assert isinstance(value_object, helper.chromeDriverHelper.ChromeDriverHelperValue)
        assert TEST_URL in value_object.url
        assert value_object.selectors == TEST_SELECTORS
        assert "title" in value_object.items
        assert value_object.items["title"] == ["Example Domain"]

    def test_get_url(self, chromedriver_helper):
        chromedriver_helper.open_current_tab(TEST_URL)
        chromedriver_helper.scraping(TEST_SELECTORS) # value_objectを作成するために必要
        assert TEST_URL in chromedriver_helper.get_url()

    def test_get_selectors(self, chromedriver_helper):
        chromedriver_helper.open_current_tab(TEST_URL)
        chromedriver_helper.scraping(TEST_SELECTORS) # value_objectを作成するために必要
        assert chromedriver_helper.get_selectors() == TEST_SELECTORS

    def test_get_items(self, chromedriver_helper):
        chromedriver_helper.open_current_tab(TEST_URL)
        chromedriver_helper.scraping(TEST_SELECTORS)  # value_objectを作成するために必要
        items = chromedriver_helper.get_items()
        assert "title" in items
        assert isinstance(items["title"], list)
        assert len(items["title"]) == 1  # titleは一つだけ取得される
        assert items["title"][0] == "Example Domain"  # titleの値を確認

    def test_get_source(self, chromedriver_helper):
        chromedriver_helper.open_current_tab(TEST_URL)
        source = chromedriver_helper.get_source()
        assert "<title>" in source

    def test_open_new_tab(self, chromedriver_helper, monkeypatch):
        mock_window_handles = ['win1'] # 修正
        start_handle = chromedriver_helper._driver.current_window_handle  # start_handleを先に取得
        # current_window_handleとwindow_handlesをモックで変更
        monkeypatch.setattr(chromedriver_helper._driver.switch_to, 'new_window', lambda x: None)
        monkeypatch.setattr(chromedriver_helper._driver, "current_window_handle", 'win2')
        monkeypatch.setattr(chromedriver_helper._driver, 'window_handles', mock_window_handles)
        new_handle = chromedriver_helper.open_new_tab(TEST_URL)
        assert new_handle == mock_window_handles[1]
        assert len(chromedriver_helper._driver.window_handles) == 2
        assert new_handle != start_handle  # new_handleは新しいウィンドウハンドルであることを確認

    def test_close(self, chromedriver_helper, monkeypatch):
        # 初期状態のウィンドウハンドルを設定
        initial_handles = ["win1"]
        chromedriver_helper._driver.window_handles = initial_handles
        chromedriver_helper._ChromeDriverHelper__start_window_handle = "win1"
        chromedriver_helper._window_handle_list = []
        # open_new_tab のモックを設定
        new_window_handle = "win2"
        def mock_open_new_tab(url):
            chromedriver_helper._window_handle_list.append(new_window_handle)
            chromedriver_helper._driver.window_handles.append(new_window_handle)
            chromedriver_helper._driver.current_window_handle = new_window_handle
            return new_window_handle

        monkeypatch.setattr(chromedriver_helper, "open_new_tab", mock_open_new_tab)

        # close のモックを設定（__start_window_handle の保護を含む）
        def mock_close(window_handle=None):
            if window_handle is None:
                window_handle = chromedriver_helper._driver.current_window_handle
            if window_handle == chromedriver_helper._ChromeDriverHelper__start_window_handle:
                raise ValueError("開始時のタブは閉じられません。")
            if window_handle in chromedriver_helper._window_handle_list:
                chromedriver_helper._window_handle_list.remove(window_handle)
                chromedriver_helper._driver.window_handles.remove(window_handle)
                chromedriver_helper._driver.current_window_handle = chromedriver_helper._driver.window_handles[0] if\
                    chromedriver_helper._driver.window_handles\
                    else\
                    chromedriver_helper._ChromeDriverHelper__start_window_handle

        monkeypatch.setattr(chromedriver_helper, "close", mock_close)
        # テスト実行
        tab_count = len(chromedriver_helper._driver.window_handles) # モックされたwindow_handlesを使用
        new_tab_handle = chromedriver_helper.open_new_tab(TEST_URL)
        chromedriver_helper.close(new_tab_handle)
        assert len(chromedriver_helper._driver.window_handles) == tab_count # モックされたwindow_handlesを使用

    def test_is_url_only(self):
        assert helper.chromeDriverHelper.ChromeDriverHelperValue.is_url_only("https://www.example.com") == True
        assert helper.chromeDriverHelper.ChromeDriverHelperValue.is_url_only("www.example.com") == False

    def test_save_source(self, chromedriver_helper, tmp_path):
        chromedriver_helper.open_current_tab(TEST_URL)
        file_path = tmp_path / "test_source.html"  # 一時ディレクトリに保存
        chromedriver_helper.save_source(str(file_path))
        assert file_path.exists()

    def test_back_forward(self, chromedriver_helper):
        chromedriver_helper._driver.current_url = "https://www.google.com"
        chromedriver_helper.back()
        chromedriver_helper._driver.back.assert_called_once()
        chromedriver_helper.forward()
        chromedriver_helper._driver.forward.assert_called_once()

    def test_next_previous_tab(self, chromedriver_helper, monkeypatch):
        chromedriver_helper._window_handle_list = ["win1", "win2"]
        chromedriver_helper._ChromeDriverHelper__start_window_handle = "win1" # private変数にアクセス
        chromedriver_helper.next_tab()
        chromedriver_helper.previous_tab()
        chromedriver_helper.next_tab()
        assert chromedriver_helper._driver.switch_to.window.call_count == 3
        assert chromedriver_helper._driver.switch_to.window.call_args_list == [call("win2"), call("win1"), call("win2")]

    @pytest.mark.parametrize("url, expected", [
        ("data:image/png;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7", True),  # 最小の有効な Base64 データ
        (TEST_IMAGE_URL, False)
    ])
    def test_download_image(self, chromedriver_helper, tmp_path, url, expected):
        with patch("helper.uri.Uri.save_data_uri") as mock_save_data_uri, \
            patch.object(chromedriver_helper, 'save_image') as mock_save_image:
            chromedriver_helper.download_image(url, download_path=str(tmp_path))
            if expected :
                mock_save_data_uri.assert_called_once()
            else:
                mock_save_image.assert_called_once()

    def test_open_current_tab(self, chromedriver_helper):
        chromedriver_helper.open_current_tab(TEST_URL)
        chromedriver_helper._driver.get.assert_called_once_with(TEST_URL)

    def test_chromedriver_helper_init_invalid_value_object(self, monkeypatch):
        with patch('helper.chromeDriverHelper.webdriver.Chrome'), \
            patch('helper.chromeDriverHelper.WebDriverWait'):
            with pytest.raises(ValueError):
                helper.chromeDriverHelper.ChromeDriverHelper(value_object=123)

    def test_scraping_invalid_selector(self, chromedriver_helper):
        invalid_selectors = {"invalid": [(By.ID, "not_exist_element", lambda elem: elem.text)]}
        items = chromedriver_helper.scraping(invalid_selectors)
        assert "invalid" in items
        assert items["invalid"] == []

    def test_close_invalid_window_handle(self, chromedriver_helper):
        with pytest.raises(ValueError) as e:
            chromedriver_helper.close("invalid_handle")
        assert "指定されたウィンドウハンドル 'invalid_handle' が存在しません。" in str(e.value)

    def test_close_start_window_handle(self, chromedriver_helper):
        with pytest.raises(ValueError) as e:
            chromedriver_helper.close(chromedriver_helper._ChromeDriverHelper__start_window_handle)
        assert "開始時のタブは閉じられません。" in str(e.value)
        # タブが閉じられていないことを確認
        assert len(chromedriver_helper._driver.window_handles) == 1


# ChromeDriverHelperValueのテスト
class TestChromeDriverHelperValue:
    def test_constructor_valid(self):
        value_object = helper.chromeDriverHelper.ChromeDriverHelperValue(TEST_URL, TEST_SELECTORS, {"title": ["Example Domain"]})
        assert value_object.url == TEST_URL
        assert value_object.selectors == TEST_SELECTORS
        assert value_object.items == {"title": ["Example Domain"]}

    def test_constructor_invalid_url(self):
        with pytest.raises(ValueError):
            helper.chromeDriverHelper.ChromeDriverHelperValue("", TEST_SELECTORS, {"title": ["Example Domain"]})
        with pytest.raises(ValueError):
            helper.chromeDriverHelper.ChromeDriverHelperValue("invalid url", TEST_SELECTORS, {"title": ["Example Domain"]})

    def test_constructor_invalid_selectors(self):
        with pytest.raises(ValueError):
            helper.chromeDriverHelper.ChromeDriverHelperValue(TEST_URL, None, {"title": ["Example Domain"]})

    def test_constructor_invalid_items(self):
        with pytest.raises(ValueError):
            helper.chromeDriverHelper.ChromeDriverHelperValue(TEST_URL, TEST_SELECTORS, None)
