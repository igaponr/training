import os
import unittest
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
        # google検索画像「カタマラン」一つ目
        self.file_name = 'カタマラン01'
        self.data_uri = "data:image/jpeg;base64,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"

    def tearDown(self):
        print("tearDown")
        del self.image_url
        del self.image_url_list

    def test___init___01(self):
        """引数無コンストラクタ"""
        with self.assertRaises(ValueError):
            webFileHelper.WebFileHelper()

    def test___init___02(self):
        """引数有コンストラクタ"""
        with self.assertRaises(ValueError):
            webFileHelper.WebFileHelper(self.image_url_list)

    def test___init___03(self):
        """引数有コンストラクタ"""
        test_target = webFileHelper.WebFileHelper(self.image_url)
        self.assertTrue(isinstance(test_target, webFileHelper.WebFileHelper))
        self.assertEqual(webFileHelper.WebFileHelper.ext_list, test_target.ext_list)
        self.assertEqual(webFileHelper.WebFileHelper.value_object, None)
        self.assertNotEqual(webFileHelper.WebFileHelper.value_object, test_target.value_object)
        self.assertEqual(webFileHelper.WebFileHelper.download_file_name, None)
        self.assertNotEqual(webFileHelper.WebFileHelper.download_file_name, test_target.get_download_file_name())
        self.assertNotEqual(webFileHelper.WebFileHelper.start_ext, None)
        self.assertEqual(webFileHelper.WebFileHelper.start_ext, test_target.get_start_ext())
        self.assertNotEqual(webFileHelper.WebFileHelper.download_path, None)
        self.assertEqual(webFileHelper.WebFileHelper.download_path, test_target.get_download_path())
        self.assertEqual(self.image_url, test_target.get_url())

    def test___init___04(self):
        """引数有コンストラクタ"""
        test_target = webFileHelper.WebFileHelper(self.data_uri, self.file_name)
        self.assertTrue(isinstance(test_target, webFileHelper.WebFileHelper))
        self.assertEqual(webFileHelper.WebFileHelper.ext_list, test_target.ext_list)
        self.assertEqual(webFileHelper.WebFileHelper.value_object, None)
        self.assertNotEqual(webFileHelper.WebFileHelper.value_object, test_target.value_object)
        self.assertEqual(webFileHelper.WebFileHelper.download_file_name, None)
        self.assertEqual(webFileHelper.WebFileHelper.download_file_name, test_target.download_file_name)
        self.assertNotEqual(webFileHelper.WebFileHelper.start_ext, None)
        self.assertEqual(webFileHelper.WebFileHelper.start_ext, test_target.start_ext)
        self.assertNotEqual(webFileHelper.WebFileHelper.download_path, None)
        self.assertEqual(webFileHelper.WebFileHelper.download_path, test_target.download_path)
        self.assertEqual(self.data_uri, test_target.get_url())

    def test_is_image(self):
        """対象URLは画像ファイルである"""
        test_target = webFileHelper.WebFileHelper(self.image_url)
        self.assertTrue(test_target.is_image())

    def test_is_exist(self):
        """対象URLのファイルはローカルに存在する"""
        test_target = webFileHelper.WebFileHelper(self.image_url)
        self.assertFalse(test_target.is_exist())

    def test_get_url(self):
        """対象URLを取得する"""
        test_target = webFileHelper.WebFileHelper(self.image_url)
        self.assertEqual(test_target.get_url(), self.image_url)

    def test_get_path(self):
        """ファイルのフルパスを得る"""
        test_target = webFileHelper.WebFileHelper(self.image_url)
        self.assertEqual(test_target.get_path(), os.path.join(test_target.get_download_path(),
                                                              test_target.get_filename() + test_target.get_ext(),
                                                              ).replace(os.sep, '/'))

    def test_get_folder_path(self):
        """フォルダーパスを得る"""
        test_target = webFileHelper.WebFileHelper(self.image_url)
        self.assertEqual(test_target.get_download_path(), test_target.value_object.download_path)

    def test_download_requests(self):
        """フォルダーパスを得る"""
        test_target = webFileHelper.WebFileHelper(self.image_url)
        test_target.download_requests()
        self.assertTrue(test_target.is_exist())
        # 後処理
        test_target.delete_local_file()


if __name__ == '__main__':
    unittest.main()

