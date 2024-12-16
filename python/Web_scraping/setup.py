from setuptools import setup, find_packages
import unittest


# def my_test_suite():
#     test_loader = unittest.TestLoader()
#     test_suite = test_loader.discover('tests', pattern='test_*.py')
#     return test_suite


def requirements_from_file(file_name):
    return open(file_name).read().splitlines()


setup(
    name='Web_scraping',  # パッケージ名
    version='1.0.0',    # バージョン
    packages=find_packages(),  # パッケージを含むディレクトリを自動検出
    package_data={'helper': ['./json/*.json']},
    url='https://github.com/igaponr/',
    license='MIT',
    author='igapon',
    author_email='igapon@gmail.com',
    install_requires=requirements_from_file('requirements.txt'),
    # tests_require=['unittest'],  # unittestが必要な場合
    # test_suite='setup.my_test_suite',
    test_suite='tests',
    # ... その他のメタデータ ...
)
