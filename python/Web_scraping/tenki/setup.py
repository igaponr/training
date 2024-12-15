import setuptools
from setuptools import setup, find_packages
import unittest


def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


setup(
    name='tenki',  # パッケージ名
    version='1.0.0',    # バージョン
    packages=find_packages(),  # パッケージを含むディレクトリを自動検出
    install_requires=[  # 依存パッケージ
        'lxml_html_clean==0.4.1',
        'pyppeteer==1.0.0'
        'requests_html==0.10.0',
        'selenium==4.27.1',
    ],
    tests_require=['unittest'], # unittestが必要な場合
    test_suite='setup.my_test_suite',
    # ... その他のメタデータ ...
)
