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
import helper.chromeDriverHelper
import helper.webFileListHelper
import helper.webFileHelper

# local source
from const import *

if __name__ == '__main__':  # インポート時には動かない
    load_path = './downloadlist.txt'
    with open(load_path, 'r', encoding='utf-8') as work_file:
        buff = work_file.readlines()
        for line in buff:
            target_url = line.rstrip('\n')
            # スクレイピングして末尾画像のナンバーから全ての画像URLを推測して展開する
            url_deployment = helper.urlDeployment.UrlDeployment(target_url, SELECTORS)
            title = url_deployment.get_title()
            url_title = helper.chromeDriverHelper.ChromeDriverHelper.fixed_file_name(target_url)
            # url_list = url_deployment.get_image_urls()
            image_items = helper.crawling.Crawling.scraping(target_url, SELECTORS)
            image_urls = helper.crawling.Crawling.take_out(image_items, 'image_urls')
            last_image_url = helper.crawling.Crawling.take_out(image_items, 'image_url')
            if not last_image_url:
                raise ValueError(f"エラー:last_image_urlが不正[{last_image_url}]")
            print(last_image_url, image_urls)
            web_file_list = helper.webFileListHelper.WebFileListHelper([last_image_url])
            # 末尾画像のナンバーから全ての画像URLを推測して展開する
            web_file_list.update_value_object_by_deployment_url_list()
            url_list = web_file_list.get_url_list()
            print(url_list)
            web_file_list = helper.webFileListHelper.WebFileListHelper(url_list)
            web_file_list.download_irvine()
            for count in enumerate(helper.webFileHelper.WebFileHelper.ext_list):
                if web_file_list.is_exist():
                    break
                # ダウンロードに失敗しているときは、失敗しているファイルの拡張子を変えてダウンロードしなおす
                web_file_list.rename_url_ext_shift()
                web_file_list.download_irvine()
            if not web_file_list.make_zip_file():
                sys.exit()
            if not web_file_list.rename_zip_file(title):
                if not web_file_list.rename_zip_file(f'{title}：{url_title}'):
                    sys.exit()
            web_file_list.delete_local_files()
