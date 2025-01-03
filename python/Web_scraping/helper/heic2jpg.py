#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
指定path以下を再帰的に検索して、見つかったHEICファイルからJPEGファイルを生成する
"""
import os
import argparse
from PIL import Image
import imagecodecs


def heic_to_jpg(heic_path, jpg_path):
    """HEIC画像をJPG画像に変換します。"""
    try:
        with open(heic_path, 'rb') as f:
            data = f.read()
        decoded_image = imagecodecs.imread(data, 'heif')
        image = Image.fromarray(decoded_image)
        image.save(jpg_path, "JPEG")
        print(f"{heic_path} を {jpg_path} に変換しました。")
    except Exception as e:
        print(f"変換エラー: {e}: {heic_path}")


def convert_all_heic_to_jpg(folder_path):
    """指定されたフォルダ内のすべてのHEICファイルをJPGに変換します。"""
    for root, _, files in os.walk(folder_path):  # サブディレクトリも処理
        for filename in files:
            if filename.lower().endswith(".heic"):
                heic_path = os.path.join(root, filename)
                jpg_path = os.path.join(root, filename[:-5] + ".jpg")
                heic_to_jpg(heic_path, jpg_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HEICファイルをJPGファイルに変換します。')
    parser.add_argument('-p', '--path', default=os.getcwd(), help='変換対象のフォルダパス。指定がない場合はカレントディレクトリ')
    args = parser.parse_args()

    target_path = args.path

    if not os.path.exists(target_path):
        print(f"エラー: 指定されたパス '{target_path}' が存在しません。")
    elif os.path.isfile(target_path):
        if target_path.lower().endswith(".heic"):
            jpg_path = target_path[:-5] + ".jpg"
            heic_to_jpg(target_path, jpg_path)
        else:
            print(f"エラー: 指定されたファイル '{target_path}' はHEICファイルではありません。")
    else:
      convert_all_heic_to_jpg(target_path)
