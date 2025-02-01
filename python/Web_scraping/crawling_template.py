#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Webサイトをクローリングし、情報をスクレイピングして画像をダウンロードするスクリプト

このスクリプトは、Seleniumを使用してWebサイトをクローリングし、指定されたセレクタを使用して情報をスクレイピングし、画像をダウンロードします
コマンドライン引数を使用して、クローリングするURL、開始ページと終了ページ、および実行するアクション（URLの追加、チェック、ダウンロード）を指定できます
また、SlackまたはLINEに通知を送信することもできます

site_selectors, page_selectors, image_selectors をクローリング対象のサイトに合わせて変更する必要があります

Attributes:
    site_selectors (dict): サイトのURLを取得するためのセレクタ
    page_selectors (dict): ページからタイトルや言語などの情報を取得するためのセレクタ
    image_selectors (dict): ページから画像URLを取得するためのセレクタ

Examples:
    サイトURLを指定して、クローリング、チェック、ダウンロードを実行する:

    ```bash
    python crawling_template.py -u https://*/?page= -a True -c True -d True
    ```

    開始ページを指定する:

    ```bash
    python crawling_template.py -s 1
    ```

    終了ページを指定する:

    ```bash
    python crawling_template.py -e 10
    ```
    slackに通知を送る

    ```bash
    python crawling_template.py -i $SLACK_CHANNEL_ID
    ```

Todo:
    * 例外処理を詳細化
    * ログ出力機能を追加
    * SlackとLINE通知の切り替え機能を実装
"""
from selenium.webdriver.common.by import By
from helper.crawling import *
from helper.slack_message_api import *

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
    """コマンドライン引数を解析する

    Returns:
        argparse.Namespace: 解析されたコマンドライン引数
    """
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
    arg_parser.add_argument('-i', '--notification_id', type=str, default="",
                            help='メッセージを送る(slack)ChannelIDや(LINE)UserIDを指定する')
    return arg_parser.parse_args()


if __name__ == '__main__':  # インポート時には動かない
    arg = get_option()
    print(arg)
    message = "crawling-end"
    try:
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
                crawling.crawling_url_deployment(page_selectors, image_selectors, arg.notification_id)
            if 'image_urls' in image_selectors:
                crawling.crawling_urls(page_selectors, image_selectors)
        print('crawling-end')
    except Exception as e:
        print(f"エラー終了しました: {e}")
        message = "crawling-error"
    # line_message_api = LineMessageAPI(access_token="", channel_secret="")
    # line_message_api.send_message(arg.user_id, message)
    slack_message_api = SlackMessageAPI(access_token="")
    slack_message_api.send_message(arg.notification_id, message)
