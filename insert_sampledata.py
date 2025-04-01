import sqlite3
import datetime
import random

def insert_sample_data():
    """
    receipts.dbにサンプルデータを挿入する関数
    10個のレシートと関連する商品データを作成
    """
    # データベースに接続
    conn = sqlite3.connect("receipts.db")
    cursor = conn.cursor()
    
    # テーブルがなければ作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store TEXT,
            genre TEXT,
            datetime TEXT,
            total REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id TEXT,
            name TEXT,
            price REAL,
            FOREIGN KEY (receipt_id) REFERENCES receipts (id)
        )
    ''')
    
    # 既存のデータをクリア（必要に応じてコメントアウト）
    cursor.execute("DELETE FROM items")
    cursor.execute("DELETE FROM receipts")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='items' OR name='receipts'")
    
    # サンプルデータ - 店舗
    stores = ["セブンイレブン", "ファミリーマート", "ローソン", "イオン", "ユニクロ", "無印良品", "スターバックス", "マクドナルド", "吉野家", "すき家"]
    
    # サンプルデータ - ジャンル
    genres = ["コンビニ", "スーパー", "衣料品", "飲食", "雑貨"]
    
    # サンプルデータ - 店舗とジャンルの対応
    store_to_genre = {
        "セブンイレブン": "コンビニ",
        "ファミリーマート": "コンビニ",
        "ローソン": "コンビニ",
        "イオン": "スーパー",
        "ユニクロ": "衣料品",
        "無印良品": "雑貨",
        "スターバックス": "飲食",
        "マクドナルド": "飲食",
        "吉野家": "飲食",
        "すき家": "飲食"
    }
    
    # サンプルデータ - 商品（店舗ごと）
    items_by_store = {
        "コンビニ": [
            ("おにぎり", 140), ("サンドイッチ", 350), ("弁当", 450), 
            ("パン", 120), ("飲料水", 140), ("コーヒー", 130), 
            ("アイス", 180), ("お菓子", 120), ("カップ麺", 210)
        ],
        "スーパー": [
            ("牛肉", 600), ("豚肉", 450), ("鶏肉", 300), 
            ("野菜セット", 350), ("果物", 400), ("魚", 550), 
            ("パスタ", 180), ("米", 2000), ("調味料", 250)
        ],
        "衣料品": [
            ("Tシャツ", 1900), ("ジーンズ", 3900), ("靴下", 790), 
            ("下着", 1200), ("パーカー", 2900), ("ジャケット", 4900), 
            ("スカート", 2400), ("ワンピース", 3900), ("帽子", 1600)
        ],
        "飲食": [
            ("コーヒー", 340), ("サンドイッチ", 480), ("ケーキ", 420), 
            ("ハンバーガー", 390), ("フライドポテト", 250), ("牛丼", 490), 
            ("定食", 750), ("うどん", 450), ("ラーメン", 850)
        ],
        "雑貨": [
            ("ノート", 350), ("ペン", 120), ("収納ボックス", 1500), 
            ("タオル", 650), ("シャンプー", 750), ("歯ブラシ", 320), 
            ("洗剤", 480), ("バスマット", 1200), ("キッチン用品", 980)
        ]
    }
    
    # 現在の日時を基準に、過去3ヶ月のランダムな日時を生成する関数
    def random_datetime_iso8601():
        current_time = datetime.datetime.now()
        days_ago = random.randint(0, 90)  # 過去90日以内
        random_date = current_time - datetime.timedelta(days=days_ago, 
                                                       hours=random.randint(0, 23), 
                                                       minutes=random.randint(0, 59))
        return random_date.strftime("%Y-%m-%dT%H:%M:%S")
    
    # レシートデータの作成と挿入
    receipt_ids = []
    for i in range(10):
        store = random.choice(stores)
        genre = store_to_genre[store]
        
        # レシートの日時（ISO8601形式）
        receipt_datetime = random_datetime_iso8601()
        
        # レシートに含まれる商品の生成
        num_items = random.randint(1, 5)  # 1~5個の商品
        receipt_items = []
        
        # ジャンルに合った商品をランダムに選択
        for _ in range(num_items):
            item_name, item_price = random.choice(items_by_store[genre])
            receipt_items.append((item_name, item_price))
        
        # 合計金額の計算
        total_amount = sum(item[1] for item in receipt_items)
        
        # レシートの挿入
        cursor.execute(
            "INSERT INTO receipts (store, genre, datetime, total) VALUES (?, ?, ?, ?)",
            (store, genre, receipt_datetime, total_amount)
        )
        
        receipt_id = cursor.lastrowid
        receipt_ids.append(receipt_id)
        
        # 商品の挿入
        for item_name, item_price in receipt_items:
            cursor.execute(
                "INSERT INTO items (receipt_id, name, price) VALUES (?, ?, ?)",
                (receipt_id, item_name, item_price)
            )
    
    # コミットして変更を保存
    conn.commit()
    
    # 基本的な情報を表示
    cursor.execute("SELECT COUNT(*) FROM receipts")
    receipt_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM items")
    item_count = cursor.fetchone()[0]
    
    # 挿入したデータの概要を取得
    cursor.execute("SELECT id, store, total FROM receipts")
    receipt_summary = cursor.fetchall()
    
    # データベース接続を閉じる
    conn.close()
    
    print(f"サンプルデータの挿入が完了しました。")
    print(f"レシート数: {receipt_count}")
    print(f"商品数: {item_count}")
    print("\nレシート概要:")
    for r in receipt_summary:
        print(f"ID: {r[0]}, 店舗: {r[1]}, 合計: {r[2]}円")
    
    return receipt_ids

if __name__ == "__main__":
    insert_sample_data()