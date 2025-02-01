import os
import sys
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import helper.chromeDriverHelper


# テスト用のダミーURLとセレクタ
TEST_URL = "https://www.example.com"
TEST_SELECTORS = {"title": [("tag name", "title", lambda elem: elem.text)]}


@pytest.fixture(scope="module", autouse=True)
def chromedriver_helper():
    """ChromeDriverHelperのインスタンスをfixtureとして提供"""
    chrome_helper = helper.chromeDriverHelper.ChromeDriverHelper()
    yield chrome_helper
    chrome_helper.destroy()


class TestChromeDriverHelper:

    def test_fixed_path(self):
        assert helper.chromeDriverHelper.ChromeDriverHelper.fixed_path("C:\\test:folder*") == "C：\\test：folder＊"

    def test_fixed_file_name(self):
        assert helper.chromeDriverHelper.ChromeDriverHelper.fixed_file_name("test/file:name*.txt") == "test／file：name＊.txt"

    def test_scraping(self, chromedriver_helper):
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

    def test_open_new_tab(self, chromedriver_helper):
        start_handle = chromedriver_helper._driver.current_window_handle
        new_handle = chromedriver_helper.open_new_tab(TEST_URL)
        assert new_handle != start_handle
        assert len(chromedriver_helper._driver.window_handles) == 2

    def test_close(self, chromedriver_helper):
        tab_count = len(chromedriver_helper._driver.window_handles)
        chromedriver_helper.open_new_tab(TEST_URL)
        chromedriver_helper.close()
        assert len(chromedriver_helper._driver.window_handles) == tab_count


    def test_is_url_only(self):
        assert helper.chromeDriverHelper.ChromeDriverHelperValue.is_url_only("https://www.example.com") == True
        assert helper.chromeDriverHelper.ChromeDriverHelperValue.is_url_only("www.example.com") == False


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
