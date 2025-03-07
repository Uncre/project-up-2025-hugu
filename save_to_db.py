import sqlite3

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

def save_to_db(response):
    conn = sqlite3.connect('receipts.db')
    cursor = conn.cursor()
    
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