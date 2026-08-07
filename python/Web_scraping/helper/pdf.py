"""
小松ゴミ捨てPDF解析
"""
import camelot
import requests
import io
import pytesseract
import re
from PIL import Image

# PDFのURL
# url = "https://www.city.komatsu.lg.jp/material/files/group/17/R7calender_no1_ja.pdf"
# url = "https://www.city.komatsu.lg.jp/material/files/group/17/R7calender_No2_ja.pdf"  # 容器包装プラが、金ではなく木と認識
# url = "https://www.city.komatsu.lg.jp/material/files/group/17/R7calender_No3_ja.pdf"
# url = "https://www.city.komatsu.lg.jp/material/files/group/17/R7calender_No4_ja.pdf"  # 容器包装プラが、金ではなく木と認識
# url = "https://www.city.komatsu.lg.jp/material/files/group/17/R7calender_No5_ja.pdf"  # 容器包装プラが、土ではなく木と認識
url = "https://www.city.komatsu.lg.jp/material/files/group/17/R7calender_No6_ja.pdf"
# url = "https://www.city.komatsu.lg.jp/material/files/group/17/R7cakender_No7_ja.pdf"  # 容器包装プラが、金ではなく木と認識
# url = "https://www.city.komatsu.lg.jp/material/files/group/17/C7calender_No8_ja.pdf"  # 容器包装プラが、土ではなく木と認識
# url = "https://www.city.komatsu.lg.jp/material/files/group/17/C7calender_No9_ja.pdf"
# url = "https://www.city.komatsu.lg.jp/material/files/group/17/R7calender_No10_ja.pdf"  # 容器包装プラが、土ではなく木と認識
# url = "https://www.city.komatsu.lg.jp/material/files/group/17/R7calendar_en_No6.pdf"  # 英語
# url = "https://www.city.komatsu.lg.jp/material/files/group/17/R7calendar_vi_No6.pdf"  # ベトナム

# PDFをダウンロード
response = requests.get(url)
response.raise_for_status() # エラーチェック
# ダウンロードしたPDFをBytesIOでファイルオブジェクトのように扱う
bytes_io = io.BytesIO(response.content)

# tables = camelot.read_pdf(bytes_io, flavor='stream')
#
# for table in tables:
#     for value in table.df.values:
#         try:
#             for text in value:
#                 if len(text) < 4:
#                     if "月" in text:
#                         print(text)
#                         print("---")
#                     elif "火" in text:
#                         print(text)
#                         print("---")
#                     elif "水" in text:
#                         print(text)
#                         print("---")
#                     elif "木" in text:
#                         print(text)
#                         print("---")
#                     elif "金" in text:
#                         print(text)
#                         print("---")
#                     elif "土" in text:
#                         print(text)
#                         print("---")
#         except Exception as e:
#             print("except", e)
#
# for table in tables:
#     for value in table.df.values:
#         try:
#             for text in value:
#                 text.replace('\n', '')
#                 if len(text) < 20:
#                     if "Thứ" in text:
#                         print(text)
#                         print("---")
#                     # if "Thứhai" in text:
#                     #     print(text)
#                     #     print("---")
#                     elif "Thứba" in text:
#                         print(text)
#                         print("---")
#                     elif "Thứtư" in text:
#                         print(text)
#                         print("---")
#                     elif "Thứnăm" in text:
#                         print(text)
#                         print("---")
#                     elif "Thứsáu" in text:
#                         print(text)
#                         print("---")
#                     elif "Thứbảy" in text:
#                         print(text)
#                         print("---")
#         except Exception as e:
#             print("except", e)
#
# for table in tables:
#     for value in table.df.values:
#         try:
#             for text in value:
#                 text.replace('\n', '')
#                 if len(text) < 100:
#                     if "Mon" in text:
#                         print(text)
#                         print("---")
#                     elif "Tue" in text:
#                         print(text)
#                         print("---")
#                     elif "Wed" in text:
#                         print(text)
#                         print("---")
#                     elif "Thu" in text:
#                         print(text)
#                         print("---")
#                     elif "Fri" in text:
#                         print(text)
#                         print("---")
#                     elif "Sat" in text:
#                         print(text)
#                         print("---")
#                     elif "BURNABLE" in text:
#                         print(text)
#                         print("---")
#                     elif "PLASTIC" in text:
#                         print(text)
#                         print("---")
#                     elif "WASTE" in text:
#                         print(text)
#                         print("---")
#         except Exception as e:
#             print("except", e)

# PDFを画像に変換 (popplerが必要)
try:
    images = []
    from pdf2image import convert_from_bytes
    images = convert_from_bytes(response.content, poppler_path=r"C:\poppler-23.11.0\Library\bin") # popplerのパスを指定
except ImportError:
    print("PDFの画像変換に失敗しました。pdf2imageとpopplerがインストールされていることを確認してください。")
    exit()
# OCRでテキストを抽出
text = ""
for img in images:
  text += pytesseract.image_to_string(img, lang="jpn")

# 正規表現で「可燃ごみ」の曜日を抽出
match = re.search(r"可燃ごみ\s*([月火水木金土日]+)", text)

if match:
  days = match.group(1)
  print(f"可燃ごみ: {days}")
else:
  print("可燃ごみの情報が見つかりませんでした。")