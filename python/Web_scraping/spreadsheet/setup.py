import setuptools
from setuptools import setup, find_packages
import unittest


def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


setup(
    name='spreadsheet',  # パッケージ名
    version='1.0.0',    # バージョン
    packages=find_packages(),  # パッケージを含むディレクトリを自動検出
    install_requires=[  # 依存パッケージ
        'gspread==6.1.4',
        'pyperclip==1.9.0',
        'oauth2client==4.1.3',
    ],
    tests_require=['unittest'], # unittestが必要な場合
    test_suite='setup.my_test_suite',
    # ... その他のメタデータ ...
)
