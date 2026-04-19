#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Todo:
    - docstringを整える
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import helper.urlDeployment
import helper.crawling
import helper.chromeDriver
import helper.webFileList
import helper.webFile

# local source
from const import *

if __name__ == '__main__':
    load_path = './downloadlist.txt'
    with open(load_path, 'r', encoding='utf-8') as work_file:
        buff = work_file.readlines()
        for line in buff:
            target_url = line.rstrip('\n')

            # スクレイピングの実行
            image_items = helper.crawling.Crawling.scraping(target_url, SELECTORS)

            # タイトルのバリデーション
            title = helper.crawling.Crawling.validate_title(image_items, 'title_jp', 'title_en')
            url_title = helper.chromeDriver.ChromeDriver.fixed_file_name(target_url)

            # 最終画像のURL取得
            last_image_url = helper.crawling.Crawling.take_out(image_items, 'image_url')
            if not last_image_url:
                raise ValueError(f"エラー:last_image_urlが不正[{last_image_url}]")

            # 画像リストの展開 (1枚のURLから1.webp~N.webpを生成)
            web_file_list = helper.webFileList.WebFileList([last_image_url])
            web_file_list.update_value_object_by_deployment_url_list()

            # ダウンロード実行
            web_file_list.download_irvine()

            # 拡張子違いのリトライ
            for _ in helper.webFile.WebFile.ext_list:
                if web_file_list.is_exist():
                    break
                web_file_list.rename_url_ext_shift()
                web_file_list.download_irvine()

            # ZIP化と後処理
            if not web_file_list.make_zip_file():
                continue  # 失敗時は次へ

            # リネーム
            if not web_file_list.rename_zip_file(title):
                web_file_list.rename_zip_file(f'{title}：{url_title}')

            # ローカルファイルの削除
            web_file_list.delete_local_files()