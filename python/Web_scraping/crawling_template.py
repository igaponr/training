#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ヘルプ参照のこと
site_selectors, page_selectors, image_selectorsをサイトに合わせて変更すること

例. site_urlを指定して、クローリングして、チェックして、ダウンロードする
> python crawling_template.py -u https://*/?page= -a add=True -c check=True -d download=True
例. 開始ページの指定
> python crawling_template.py -s start=1
例. 終了ページの指定
> python crawling_template.py -e end=10
"""
import copy

from argparse import ArgumentParser

from crawling import *

site_selectors = {
    Crawling.URLS_TARGET: [
        (By.XPATH,
         '//body/div[2]/div/div/a',
         lambda el: el.get_attribute("href")
         ),
    ]
}
page_selectors = {
    'title_jp': [(By.XPATH,
                  '//div/div/div/h2',
                  lambda el: el.text),
                 ],
    'title_en': [(By.XPATH,
                  '//div/div/div/h1',
                  lambda el: el.text),
                 ],
    'languages': [(By.XPATH,
                   '//div/div/section/div[6]/span/a/span[1]',
                   lambda el: el.text),
                  ],
}
image_selectors = {
    'image_url': [(By.XPATH,
                   '(//*[@id="thumbnail-container"]/div/div/a)[last()]',
                   lambda el: el.get_attribute("href")),
                  (By.XPATH,
                   '//*[@id="image-container"]/a/img',
                   lambda el: el.get_attribute("src")),
                  ],
    # 'image_urls': [(By.XPATH,
    #                 '//*[@id="thumbnail-container"]/div/div/a',
    #                 lambda el: el.get_attribute("href")),
    #                (By.XPATH,
    #                 '//*[@id="image-container"]/a/img',
    #                 lambda el: el.get_attribute("src")),
    #                ],
}


def get_option():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-a', '--add', type=bool, default=False,
                            help='クローリングしてurlリスト[crawling_list.txt]を作成する')
    arg_parser.add_argument('-c', '--check', type=bool, default=False,
                            help='urlリスト[crawling_list.txt]から処理済みurlを除外する')
    arg_parser.add_argument('-d', '--download', type=bool, default=False,
                            help='urlリスト[crawling_list.txt]のurlをスクレイピングする')
    arg_parser.add_argument('-s', '--start', type=int, default=1,
                            help='クローリング開始ページ数')
    arg_parser.add_argument('-e', '--end', type=int, default=11,
                            help='クローリング終了ページ数')
    arg_parser.add_argument('-u', '--url', type=str, default="http://*/?page=",
                            help='クローリング基準URL(http://*/?page=)')
    return arg_parser.parse_args()


if __name__ == '__main__':  # インポート時には動かない
    arg = get_option()
    print(arg)
    if arg.add:
        start_page_number = arg.start
        end_page_number = arg.end
        page_root_url = arg.url
        site_url_list = [page_root_url + str(x) for x in range(start_page_number, end_page_number)]
        crawling = None
        for site_url in site_url_list:
            crawling_items = Crawling.scraping(site_url, site_selectors)
            crawling = Crawling(site_url, site_selectors, crawling_items)
            crawling.load_text(site_selectors, Crawling.crawling_file_path)
            crawling.save_text()
    if arg.check:
        crawling = Crawling(site_selectors)
        crawling.marge_crawling_items()
    if arg.download:
        crawling = Crawling(site_selectors)
        if 'image_url' in image_selectors:
            crawling.crawling_url_deployment(page_selectors, image_selectors)
        if 'image_urls' in image_selectors:
            crawling.crawling_urls(page_selectors, image_selectors)
    print('crawling-end')
