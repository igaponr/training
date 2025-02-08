#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import helper.tenki
import helper.spreadsheet

if __name__ == '__main__':  # インポート時には動かない
    RESULT_FILE_PATH = './result.txt'
    main_url = "https://tenki.jp/forecast/4/20/5620/17202/10days.html"
    main_css_root = "dd.forecast10days-actab"
    main_css_selectors = {"days_item": "div.days",
                          "time_item": "dd.time-item > span",
                          "forecast_item": "dd.forecast-item > p > img",
                          "prob_precip_item": "dd.prob-precip-item > span > span",
                          "precip_item": "dd.precip-item > span > span",
                          "temp_item": "dd.temp-item > script",
                          "wind_item_blow": "dd.wind-item > p > img",
                          "wind_item_speed": "dd.wind-item > p > span",
                          }
    main_attrs = {"days_item": "",
                  "time_item": "",
                  "forecast_item": "alt",
                  "prob_precip_item": "",
                  "precip_item": "",
                  "temp_item": "",
                  "wind_item_blow": "alt",
                  "wind_item_speed": "",
                  }
    tenki1 = helper.tenki.Tenki(main_url,
                                main_css_root,
                                main_css_selectors,
                                main_attrs,
                                )
    # tenki1.save_text(RESULT_FILE_PATH + 'tenki1.txt')
    json_keyfile_name = (os.path.dirname(__file__) + r"\json\tenki-347610-1bc0fec79f90.json")
    workbook_name = '天気予報'

    # worksheet_name = '七尾市和倉町data'
    # spreadsheet1 = helper.spreadsheet.Spreadsheet(json_keyfile_name,
    #                                               workbook_name,
    #                                               worksheet_name,
    #                                               )
    # # spreadsheet1.save_text(RESULT_FILE_PATH + 'spreadsheet1.txt')
    # spreadsheet1.clear_worksheet()
    # spreadsheet1.write_dict_columns(tenki1.get_result_forecasts(), (1, 1))
    # main_num = len(tenki1.get_result_forecasts())
    # spreadsheet1.write_dict_columns(tenki1.get_result_counters(), (1, 1 + main_num))

    # worksheet_name = '七尾市和倉町conv'
    # spreadsheet1 = helper.spreadsheet.Spreadsheet(json_keyfile_name,
    #                                               workbook_name,
    #                                               worksheet_name,
    #                                               )
    # # spreadsheet1.save_text(RESULT_FILE_PATH + 'spreadsheet2.txt')
    # tenki1.special_func_temp()
    # spreadsheet1.clear_worksheet()
    # spreadsheet1.write_dict_columns(tenki1.get_result_forecasts(), (1, 1))
    # main_num = len(tenki1.get_result_forecasts())
    # spreadsheet1.write_dict_columns(tenki1.get_result_counters(), (1, 1 + main_num))

    worksheet_name = '七尾市和倉町'
    spreadsheet1 = helper.spreadsheet.Spreadsheet(json_keyfile_name,
                                                  workbook_name,
                                                  worksheet_name,
                                                  )
    # spreadsheet1.save_text(RESULT_FILE_PATH + 'spreadsheet3.txt')
    spreadsheet1.clear_worksheet()
    spreadsheet1.write_dict_columns(tenki1.create_LINE_BOT_TOBA_format(), (1, 1))

    main_url = "https://tenki.jp/forecast/4/19/5520/16211/10days.html"
    worksheet_name = '射水市海竜町'
    tenki1 = helper.tenki.Tenki(main_url,
                   main_css_root,
                   main_css_selectors,
                   main_attrs,
                   )
    spreadsheet1 = helper.spreadsheet.Spreadsheet(json_keyfile_name,
                                                  workbook_name,
                                                  worksheet_name,
                                                  )
    # spreadsheet1.save_text(RESULT_FILE_PATH + 'spreadsheet4.txt')
    spreadsheet1.clear_worksheet()
    spreadsheet1.write_dict_columns(tenki1.create_LINE_BOT_TOBA_format(), (1, 1))
