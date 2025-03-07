import base64
import httpx
import json
import os
import google.generativeai as genai
from PIL import Image
import sqlite3

genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# 画像をリサイズする
def resize_image(image_path):
    image = Image.open(image_path)
    (width, height) = (image.width, image.height)

    # 画像が大きい場合はリサイズする
    if width >= 1200 or height >= 1200:

        # 画像の縦横比を保ったまま、長辺が1200pxになるようにリサイズする
        if width > height:
            new_width = 1200
            new_height = int((new_width / width) * height)
        else:
            new_height = 1200
            new_width = int((new_height / height) * width)

        image = image.resize((new_width, new_height))

        # リサイズした画像を保存する
        image.save(image_path)


def post_image(image_path):
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    # ストラクチャアウトプット(AIにjson形式で出力させる)
    # iso8601
    # 小計（税抜き）
    # 税金
    # 合計
    # 店名
    # 個数
    # 長いレシートはどうする？
    # 大まかなジャンルも出力するとよいかもしれない
    prompt = """画像にはレシートが含まれています。レシートの内容をjson形式で出力してください\n
            例：\n
            {   
                "store": "store_name",
                "datetime": iso8601の日時,
                "total": （税込みの）合計金額,
                "items": [
                    {"name": "item1", "price": 500, "quantity": 2},
                    {"name": "item2", "price": 500, "quantity": 1}
                ]
            }
            もし画像にレシートが含まれていない場合は、その旨を出力してください\n
            例：\n  レシートが含まれていません\n

            """

    response = model.generate_content([
    {'mime_type': 'image/jpeg', 'data': base64.b64encode(image_data).decode('utf-8')}, 
    prompt
    ])

    # レスポンスの整形
    try:
        json_str = response.text.strip('```json\n').strip('```')
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise Exception("レシートが含まれていません")


