#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
検証コード
"""
import os
import unittest
from const import *
from tenki.tenki.tenki import *


class TestSpreadsheet(unittest.TestCase):
    """ unitテスト
    """

    def setUp(self):
        print("setUp")
        self.json_keyfile_name = (os.path.dirname(__file__) + r"\..\..\json\tenki-347610-1bc0fec79f90.json")
        self.workbook_name = '天気予報'
        self.worksheet_name = '七尾市和倉町data'
        self.spreadsheet = Spreadsheet(self.json_keyfile_name,
                                       self.workbook_name,
                                       self.worksheet_name,
                                       )

    def tearDown(self):
        print("tearDown")

    def test_tenki01(self):
        css_root = "dd.forecast10days-actab"
        css_selectors = {"days_item": "div.days",
                         "time_item": "dd.time-item > span",
                         "forecast_item": "dd.forecast-item > p > img",
                         "prob_precip_item": "dd.prob-precip-item > span > span",
                         "precip_item": "dd.precip-item > span > span",
                         "temp_item": "dd.temp-item > script",
                         "wind_item_blow": "dd.wind-item > p > img",
                         "wind_item_speed": "dd.wind-item > p > span",
                         }
        attrs = {"days_item": "",
                 "time_item": "",
                 "forecast_item": "alt",
                 "prob_precip_item": "",
                 "precip_item": "",
                 "temp_item": "",
                 "wind_item_blow": "alt",
                 "wind_item_speed": "",
                 }
        tenki = Tenki("https://tenki.jp/forecast/4/20/5620/17202/10days.html",
                      css_root,
                      css_selectors,
                      attrs,
                      )
        tenki.save_text(RESULT_FILE_PATH + '1.txt')
        # 値オブジェクトを生成
        value_objects = tenki.get_value_objects()
        # 値オブジェクトでインスタンス作成
        tenki2 = Tenki(value_objects)
        # 保存や読込を繰り返す
        tenki2.save_text(RESULT_FILE_PATH + '2.txt')
        tenki2.load_text(RESULT_FILE_PATH + '2.txt')
        tenki2.save_text(RESULT_FILE_PATH + '3.txt')
        tenki3 = Tenki()
        tenki3.load_text(RESULT_FILE_PATH + '3.txt')
        tenki3.save_text(RESULT_FILE_PATH + '4.txt')

    def test_tenki02(self):
        tenki = Tenki()
        tenki.load_text(RESULT_FILE_PATH + '1.txt')
        worksheet_name = '七尾市和倉町data'
        spreadsheet = Spreadsheet(self.json_keyfile_name,
                                  self.workbook_name,
                                  worksheet_name,
                                  )
        spreadsheet.save_text(RESULT_FILE_PATH + '2.txt')
        spreadsheet.write_dict_columns(tenki.get_result_forecasts(), (1, 1))
        num = len(tenki.get_result_forecasts())
        spreadsheet.write_dict_columns(tenki.get_result_counters(), (1, 1 + num))
        worksheet_name = '七尾市和倉町conv'
        spreadsheet = Spreadsheet(self.json_keyfile_name,
                                  self.workbook_name,
                                  worksheet_name,
                                  )
        spreadsheet.save_text(RESULT_FILE_PATH + '3.txt')
        tenki.special_func_temp()
        spreadsheet.write_dict_columns(tenki.get_result_forecasts(), (1, 1))
        num = len(tenki.get_result_forecasts())
        spreadsheet.write_dict_columns(tenki.get_result_counters(), (1, 1 + num))
        spreadsheet.save_text(RESULT_FILE_PATH + '4.txt')
        tenki.save_text(RESULT_FILE_PATH + '5.txt')

    def test_tenki03(self):
        tenki = Tenki()
        tenki.load_text(RESULT_FILE_PATH + '1.txt')
        tenki.special_func_temp()
        tenki.create_LINE_BOT_TOBA_format()


if __name__ == "__main__":
    unittest.main()
