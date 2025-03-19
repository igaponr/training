#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
検証コード
"""
import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import helper.tenki
import helper.spreadsheet

RESULT_FILE_PATH = './result'  # タイトルと、ダウンロードするファイルのURLの列挙を書き込むファイル


class TestTenkiKairyu(unittest.TestCase):
    def setUp(self):
        print("setUp")
        self.json_keyfile_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              '../../../json/tenki-347610-1bc0fec79f90.json').replace(os.sep, '/')
        self.workbook_name = '天気予報'
        self.worksheet_name = '射水市海竜町data'
        self.spreadsheet = helper.spreadsheet.Spreadsheet(self.json_keyfile_name,
                                                          self.workbook_name,
                                                          self.worksheet_name,
                                                          )

    def tearDown(self):
        print("tearDown")

    def test_tenki(self):
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
        tenki1 = helper.tenki.Tenki("https://tenki.jp/forecast/4/19/5520/16211/10days.html",
                                    css_root=css_root,
                                    css_selectors=css_selectors,
                                    attrs=attrs,
                                    )
        tenki1.save_text(RESULT_FILE_PATH + self.worksheet_name + 'tenki1.txt')
        tenki1.special_func_temp()
        tenki1.create_line_bot_toba_format()
        self.spreadsheet.write_dict_columns(tenki1.get_result_forecasts(), (1, 1))
        num = len(tenki1.get_result_forecasts())
        self.spreadsheet.write_dict_columns(tenki1.get_result_counters(), (1, 1 + num))
        self.spreadsheet.save_text(RESULT_FILE_PATH + self.worksheet_name + 'spreadsheet1.txt')
        worksheet_name = '射水市海竜町conv'
        self.spreadsheet = helper.spreadsheet.Spreadsheet(self.json_keyfile_name,
                                                          self.workbook_name,
                                                          worksheet_name,
                                                          )
        self.spreadsheet.write_dict_columns(tenki1.create_line_bot_toba_format(), (1, 1))
        self.spreadsheet.save_text(RESULT_FILE_PATH + worksheet_name + 'spreadsheet2.txt')

class TestTenkiWakura(unittest.TestCase):
    def setUp(self):
        print("setUp")
        self.json_keyfile_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              '../../../json/tenki-347610-1bc0fec79f90.json').replace(os.sep, '/')
        self.workbook_name = '天気予報'
        self.worksheet_name = '七尾市和倉町data'
        self.spreadsheet = helper.spreadsheet.Spreadsheet(self.json_keyfile_name,
                                                          self.workbook_name,
                                                          self.worksheet_name,
                                                          )
        self.css_root = "dd.forecast10days-actab"
        self.css_selectors = {"days_item": "div.days",
                              "time_item": "dd.time-item > span",
                              "forecast_item": "dd.forecast-item > p > img",
                              "prob_precip_item": "dd.prob-precip-item > span > span",
                              "precip_item": "dd.precip-item > span > span",
                              "temp_item": "dd.temp-item > script",
                              "wind_item_blow": "dd.wind-item > p > img",
                              "wind_item_speed": "dd.wind-item > p > span",
                              }
        self.attrs = {"days_item": "",
                      "time_item": "",
                      "forecast_item": "alt",
                      "prob_precip_item": "",
                      "precip_item": "",
                      "temp_item": "",
                      "wind_item_blow": "alt",
                      "wind_item_speed": "",
                      }

    def tearDown(self):
        print("tearDown")

    def test_tenki(self):
        tenki1 = helper.tenki.Tenki("https://tenki.jp/forecast/4/20/5620/17202/10days.html",
                                    css_root=self.css_root,
                                    css_selectors=self.css_selectors,
                                    attrs=self.attrs,
                                    )
        tenki1.save_text(RESULT_FILE_PATH + self.worksheet_name + 'tenki1.txt')
        tenki1.special_func_temp()
        tenki1.create_line_bot_toba_format()
        self.spreadsheet.write_dict_columns(tenki1.get_result_forecasts(), (1, 1))
        num = len(tenki1.get_result_forecasts())
        self.spreadsheet.write_dict_columns(tenki1.get_result_counters(), (1, 1 + num))
        self.spreadsheet.save_text(RESULT_FILE_PATH + self.worksheet_name + 'spreadsheet1.txt')
        worksheet_name = '七尾市和倉町conv'
        self.spreadsheet = helper.spreadsheet.Spreadsheet(self.json_keyfile_name,
                                                      self.workbook_name,
                                                      worksheet_name,
                                                      )
        self.spreadsheet.write_dict_columns(tenki1.create_line_bot_toba_format(), (1, 1))
        self.spreadsheet.save_text(RESULT_FILE_PATH + worksheet_name + 'spreadsheet2.txt')

if __name__ == "__main__":
    unittest.main()
