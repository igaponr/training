import unittest
from helper import webFileListHelper
from helper import webFileHelper


class MyTestCase(unittest.TestCase):

    def setUp(self):
        print("setup")
        # テスト　若者 | かわいいフリー素材集 いらすとや
        self.image_url = 'https://1.bp.blogspot.com/-tzoOQwlaRac/X1LskKZtKEI/AAAAAAABa_M/'\
                         '89phuGIVDkYGY_uNKvFB6ZiNHxR7bQYcgCNcBGAsYHQ/'\
                         's180-c/fashion_dekora.png'
        self.image_url_list = [
            'https://1.bp.blogspot.com/-tzoOQwlaRac/X1LskKZtKEI/AAAAAAABa_M/'
            '89phuGIVDkYGY_uNKvFB6ZiNHxR7bQYcgCNcBGAsYHQ/'
            's180-c/fashion_dekora.png',
            'https://1.bp.blogspot.com/-gTf4sWnRdDw/X0B4RSQQLrI/AAAAAAABarI/'
            'MJ9DW90dSVwtMjuUoErxemnN4nPXBnXUwCNcBGAsYHQ/'
            's180-c/otaku_girl_fashion.png',
            'https://1.bp.blogspot.com/-K8DEj7le73Y/XuhW_wO41mI/AAAAAAABZjQ/'
            'NMEk02WcUBEVBDsEJpCxTN6T0NmqG20qwCNcBGAsYHQ/'
            's180-c/kesyou_jirai_make.png',
        ]

    def tearDown(self):
        print("tearDown")
        del self.image_url
        del self.image_url_list

    def test___init___01(self):
        """引数無コンストラクタ"""
        with self.assertRaises(ValueError):
            webFileListHelper.WebFileListHelper()

    def test___init___02(self):
        """引数有コンストラクタ"""
        with self.assertRaises(ValueError):
            webFileListHelper.WebFileListHelper(self.image_url)

    def test___init___03(self):
        """引数有コンストラクタ"""
        test_target = webFileListHelper.WebFileListHelper(self.image_url_list)
        self.assertTrue(isinstance(test_target, webFileListHelper.WebFileListHelper))
        self.assertTrue(isinstance(test_target.value_object, webFileListHelper.WebFileListHelperValue))
        self.assertEqual(webFileListHelper.WebFileListHelper.value_object, None)
        self.assertNotEqual(webFileListHelper.WebFileListHelper.value_object, test_target.value_object)
        self.assertNotEqual(webFileListHelper.WebFileListHelper.download_path, None)
        self.assertEqual(webFileListHelper.WebFileListHelper.download_path, test_target.download_path)
        self.assertNotEqual(webFileListHelper.WebFileListHelper.start_ext, None)
        self.assertEqual(webFileListHelper.WebFileListHelper.start_ext, test_target.start_ext)

    def test___init___04(self):
        """引数有コンストラクタ"""
        __web_file_list_helper = webFileListHelper.WebFileListHelper(self.image_url_list)
        test_target = webFileListHelper.WebFileListHelper(__web_file_list_helper.value_object)
        self.assertTrue(isinstance(test_target, webFileListHelper.WebFileListHelper))
        self.assertTrue(isinstance(test_target.value_object, webFileListHelper.WebFileListHelperValue))
        self.assertNotEqual(webFileListHelper.WebFileListHelper.value_object, test_target.value_object)
        self.assertEqual(webFileListHelper.WebFileListHelper.download_path, test_target.download_path)

    def test_get_web_file_list(self):
        """ファイルリストを得る"""
        test_target = webFileListHelper.WebFileListHelper(self.image_url_list)
        __web_file_list = test_target.get_web_file_list()
        for web_file in __web_file_list:
            self.assertTrue(isinstance(web_file, webFileHelper.WebFileHelper))

    def test_is_exist(self):
        """対象URLのファイルはローカルに存在する"""
        test_target = webFileListHelper.WebFileListHelper(self.image_url_list)
        self.assertFalse(test_target.is_exist())

    def test_download_requests(self):
        """対象URLリストのファイルをrequestsでダウンロードする"""
        test_target = webFileListHelper.WebFileListHelper(self.image_url_list)
        test_target.download_requests()
        self.assertTrue(test_target.is_exist())
        # 後処理
        test_target.delete_local_files()
        self.assertFalse(test_target.is_exist())

    def test_download_irvine(self):
        """対象URLリストのファイルをirvineでダウンロードする"""
        test_target = webFileListHelper.WebFileListHelper(self.image_url_list)
        test_target.download_irvine()
        self.assertTrue(test_target.is_exist())
        # 後処理
        test_target.delete_local_files()
        self.assertFalse(test_target.is_exist())

    def test_download_chrome_driver(self):
        """対象URLリストのファイルをchromeDriverでダウンロードする"""
        test_target = webFileListHelper.WebFileListHelper(self.image_url_list)
        test_target.download_chrome_driver()
        self.assertTrue(test_target.is_exist())
        # 後処理
        test_target.delete_local_files()
        self.assertFalse(test_target.is_exist())


if __name__ == '__main__':
    unittest.main()
