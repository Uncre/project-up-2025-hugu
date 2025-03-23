import base64
import json
import os
import google.generativeai as genai
from PIL import Image
import sqlite3
import glob
import shutil

# 画像をリサイズする いらない？
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


def post_image(folder_path, api_key, is_discord=False) -> list:

    # フォルダパスの設定
    if folder_path == "":
        folder_path = "images"

    # APIキーの設定
    # 空の場合は環境変数から取得する
    if api_key == "":
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    else:
        genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.0-flash")
    
    # 画像ファイルのパスを取得する
    folder_path = os.path.join(folder_path, "*.jpg")
    image_list = glob.glob(folder_path)
    if len(image_list) == 0:
        raise Exception("画像が見つかりません")

    response_list = []

    # 画像を1枚ずつ処理する
    for image_path in image_list:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        # ストラクチャアウトプット(AIにjson形式で出力させる)
        # iso8601
        # 小計（税抜き）
        # 税金
        # 合計
        # 店名
        # 個数
        # 長いレシートはどうする？とりま一枚で行けるか検証
        # 大まかなジャンルも出力するとよいかもしれない

        prompt = """画像にはレシートが含まれています。レシートの内容をjson形式で出力してください\n
                    また、genreには商品やサービスの内容から判断して、適切なジャンル名を出力してください\n
                例：\n
                {   
                    "store": "店名",
                    "genre": "ジャンル名（食品、書籍、家電etc...）",
                    "datetime": "iso8601の日時",
                    "total": （税込みの）合計金額,
                    "items": [
                        {"name": "item1", "price": 500},
                        {"name": "item2", "price": 500}
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
            print(json_str)

            # レスポンスをリストに追加
            response_list.append(json.loads(json_str))

            # discordからのリクエストでない場合は画像を削除する
            if not is_discord:
                # 処理が成功した画像を別フォルダに移動する
                os.makedirs("success", exist_ok=True)
                shutil.move(image_path, "success")
            
        except json.JSONDecodeError:
            raise Exception("レシートが含まれていません")
    
    return response_list

# テスト
# post_image(R"C:\Users\hugu\Desktop\python\receipt_kanri\images\image.jpg")


# 以下、データベースへの保存処理

def init_db():
    conn = sqlite3.connect('receipts.db')
    cursor = conn.cursor()
    
    # レシート一覧テーブルの作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store TEXT,
            genre TEXT,
            datetime TEXT,
            total REAL
        )
    ''')
    
    # 商品詳細テーブルの作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id TEXT,
            name TEXT,
            price REAL,
            FOREIGN KEY (receipt_id) REFERENCES receipts (id)
        )
    ''')

    conn.commit()
    conn.close()

def save_to_db(response_list: list):
    conn = sqlite3.connect('receipts.db')
    cursor = conn.cursor()
    
    for response in response_list:
        # レシート情報の保存
        cursor.execute('''
            INSERT INTO receipts (store, genre, datetime, total)
            VALUES (?, ?, ?, ?)
        ''', (response['store'], response['genre'], response['datetime'], response['total']))
        
        # レシートIDの取得
        receipt_id = cursor.lastrowid

        # 商品情報の保存
        for item in response['items']:
            cursor.execute('''
                INSERT INTO items (receipt_id, name, price)
                VALUES (?, ?, ?)
            ''', (receipt_id, item['name'], item['price']))

        print(f"レシート情報をデータベースに保存しました: {receipt_id}")
    
    conn.commit()
    conn.close()


def main_process(folder_path, api_key, is_discord=False):
    response = post_image(folder_path, api_key)
    init_db()
    save_to_db(response)
    return json.dumps(response, indent=4, ensure_ascii=False)