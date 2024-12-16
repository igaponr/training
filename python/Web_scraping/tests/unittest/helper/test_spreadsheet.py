#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
検証コード
"""
import os
import copy
import unittest
from helper import spreadsheet

RESULT_FILE_PATH = './result.txt'  # タイトルと、ダウンロードするファイルのURLの列挙を書き込むファイル


class TestSpreadsheet(unittest.TestCase):
    """ unitテスト
    """

    def setUp(self):
        print("setUp")
        self.json_keyfile_name = (os.path.dirname(__file__) + r"\..\..\..\json\tenki-347610-1bc0fec79f90.json")
        self.workbook_name = '天気予報'
        self.worksheet_name = '七尾市和倉町data'
        self.spreadsheet = spreadsheet.Spreadsheet(self.json_keyfile_name,
                                                   self.workbook_name,
                                                   self.worksheet_name,
                                                   )

    def tearDown(self):
        print("tearDown")

    def test_spreadsheet01(self):
        """
        読込からのインスタンス生成
        :return:
        """
        self.spreadsheet.save_text(RESULT_FILE_PATH + '1.txt')
        spreadsheet2 = copy.deepcopy(self.spreadsheet)
        self.spreadsheet.load_text(RESULT_FILE_PATH + '1.txt')
        self.assertEqual(self.spreadsheet, spreadsheet2)

    def test_spreadsheet02(self):
        """
        値オブジェクトからのインスタンス生成
        :return:
        """
        value_objects = self.spreadsheet.get_value_objects()
        spreadsheet2 = spreadsheet.Spreadsheet(value_objects)
        self.assertEqual(self.spreadsheet, spreadsheet2)

    def test_spreadsheet03(self):
        """

        :return:
        """
        spreadsheet3 = spreadsheet.Spreadsheet()
        spreadsheet3.load_text(RESULT_FILE_PATH + '1.txt')
        spreadsheet3.write_list_columns([100, 200, 300, 50], (1, 1))
        spreadsheet3.write_list_columns([99, 98, 97, 96], (1, 3))
        spreadsheet3.write_list_rows([1, 2, 3, 4], (5, 5))
        spreadsheet3.write_list_rows([10, 20, 30, 40], (7, 5))
        tenki = {
            "days_item": ["04月17日(日)", "04月18日(月)", "04月19日(火)", "04月20日(水)", "04月21日(木)", "04月22日(金)", "04月23日(土)",
                          "04月24日(日)", "04月25日(月)", "04月26日(火)", "04月27日(水)", "04月28日(木)", "04月29日(金)", "04月30日(土)"],
            "time_item": ["00", "06", "12", "18", "24", "00", "06", "12", "18", "24", "00", "06", "12", "18", "24",
                          "00", "06", "12", "18", "24", "00", "06", "12", "18", "24", "00", "06", "12", "18", "24",
                          "00", "06", "12", "18", "24", "00", "06", "12", "18", "24", "00", "06", "12", "18", "24",
                          "00", "06", "12", "18", "24", "00", "06", "12", "18", "24"],
            "forecast_item": ["晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "曇", "曇", "曇のち雨",
                              "雨", "雨のち曇", "曇のち晴", "晴", "晴", "晴", "晴", "曇", "曇", "曇", "曇", "曇のち晴", "晴", "晴", "晴",
                              "晴のち曇", "曇のち雨", "雨のち晴", "晴", "晴", "晴", "晴", "曇", "曇"],
            "prob_precip_item": ["0%", "10%", "10%", "10%", "10%", "10%", "0%", "0%", "0%", "0%", "0%", "0%", "0%",
                                 "20%", "40%", "40%", "70%", "90%", "70%", "40%", "20%", "20%", "20%", "20%", "50%",
                                 "50%", "50%", "40%", "30%", "10%", "20%", "20%", "30%", "60%", "60%", "0%", "0%",
                                 "0%", "20%", "40%", "40%"],
            "precip_item": ["0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜",
                            "0㎜", "1㎜", "12㎜", "1㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜",
                            "0㎜", "0㎜", "0㎜", "4㎜", "4㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜"],
            "wind_item_blow": ["南", "南", "南", "南南西", "南西", "南", "南南西", "南南西", "北東", "北東", "東北東", "南", "南", "南", "北東",
                               "南南東", "南南東", "南南東", "南", "南西", "東", "南南東", "南南東", "東北東", "北北東", "南南西", "南西", "南西",
                               "南西", "南西", "西南西", "西", "西", "東", "北東", "北北東", "西南西", "西南西", "南西", "南西", "南", "南西",
                               "南西", "西南西", "西北西", "西", "南西", "南西", "南西", "西南西", "西南西"],
            "wind_item_speed": ["2m/s", "1m/s", "1m/s", "1m/s", "3m/s", "1m/s", "1m/s", "1m/s", "2m/s", "2m/s", "1m/s",
                                "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "2m/s", "1m/s", "2m/s", "2m/s",
                                "2m/s", "1m/s", "2m/s", "2m/s", "3m/s", "3m/s", "4m/s", "5m/s", "3m/s", "1m/s", "1m/s",
                                "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "4m/s", "4m/s", "5m/s",
                                "4m/s", "2m/s", "2m/s", "2m/s", "2m/s", "2m/s", "3m/s"]}
        spreadsheet3.write_dict_columns(tenki, (10, 10))
        spreadsheet3.write_dict_rows(tenki, (10, 17))


if __name__ == "__main__":
    unittest.main()
