import unittest
from helper import irvineHelper
from helper import webFileListHelper


class MyTestCase(unittest.TestCase):

    def setUp(self):
        print("setup")
        # TODO: gitに画像アップロードして、その画像ダウンロードに変更する
        self.image_url_list = [
            'https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhwQ0Rt_D5XNRWZ9ml1fe39qosoTwotUwGotjtghs17btdS'
            '-iHGkU_2-05n56v3XRZoNfQ-FO7zNUNRDxdTkFvJhqvhlHwoaUyjrCyzEiOFPJ568w3PFs31k_z89fQ0eNppyrb93-26KTf1/s1600/'
            'otaku_girl_fashion.png',
            'https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj63FCXO9wlu6gqqojDu2wd9mJ_'
            'mL79qiPGkZNsA1QMsKRoShnVY0FjHkDqKL74sOH29Gnm-HfcjVYswCAU1UtRoaMC4NcBmvhrrJmBXs2omwpk8d4azpN3u3l5darnFLvg'
            'WVac0_tH82Ef/s1600/kesyou_jirai_make.png',
        ]
        self.download_file_name = [
            '0000.png',
            '0001.png',
        ]

    def tearDown(self):
        print("tearDown")
        del self.image_url_list
        del self.download_file_name

    def test___init___01(self):
        """引数無コンストラクタ"""
        with self.assertRaises(ValueError):
            irvineHelper.IrvineHelper()

    def test___init___02(self):
        """引数有コンストラクタ"""
        with self.assertRaises(ValueError):
            irvineHelper.IrvineHelper("test.txt")

    def test___init___03(self):
        """引数有コンストラクタ"""
        with self.assertRaises(ValueError):
            irvineHelper.IrvineHelper(irvineHelper.IrvineHelper.list_path, "test.txt")

    def test___init___04(self):
        """引数有コンストラクタ"""
        test_target = irvineHelper.IrvineHelper(self.image_url_list)
        self.assertTrue(isinstance(test_target, irvineHelper.IrvineHelper))
        self.assertEqual(irvineHelper.IrvineHelper.list_path, test_target.list_path)
        self.assertEqual(irvineHelper.IrvineHelper.running, test_target.running)
        self.assertNotEqual(irvineHelper.IrvineHelper.value_object, test_target.value_object)
        self.assertEqual(irvineHelper.IrvineHelper.list_path, test_target.value_object.list_path)
        self.assertEqual(irvineHelper.IrvineHelperValue.exe_path, test_target.value_object.exe_path)

    def test___init___05(self):
        """引数有コンストラクタ"""
        __irvine_helper = irvineHelper.IrvineHelper(self.image_url_list)
        test_target = irvineHelper.IrvineHelper(__irvine_helper.value_object)
        self.assertTrue(isinstance(test_target, irvineHelper.IrvineHelper))
        self.assertEqual(irvineHelper.IrvineHelper.list_path, test_target.list_path)
        self.assertEqual(irvineHelper.IrvineHelper.running, test_target.running)
        self.assertNotEqual(irvineHelper.IrvineHelper.value_object, test_target.value_object)
        self.assertEqual(irvineHelper.IrvineHelper.list_path, test_target.value_object.list_path)
        self.assertEqual(irvineHelper.IrvineHelperValue.exe_path, test_target.value_object.exe_path)

    def test_download_01(self):
        """ダウンロード"""
        test_target = irvineHelper.IrvineHelper(self.image_url_list)
        test_target.download()
        __test_target = webFileListHelper.WebFileListHelper(self.image_url_list)
        self.assertTrue(__test_target.is_exist())
        # 後処理
        __test_target.delete_local_files()
        self.assertFalse(__test_target.is_exist())

    def test_download_02(self):
        """ダウンロード"""
        test_target = irvineHelper.IrvineHelper(self.image_url_list, None, self.download_file_name)
        test_target.download()
        __test_target = webFileListHelper.WebFileListHelper(self.image_url_list)
        self.assertTrue(__test_target.is_exist())
        # 後処理
        __test_target.delete_local_files()
        self.assertFalse(__test_target.is_exist())


if __name__ == '__main__':
    unittest.main()
