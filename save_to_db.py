import sqlite3
import uuid

def init_db():
    conn = sqlite3.connect('receipts.db')
    cursor = conn.cursor()
    
    # レシート一覧テーブルの作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id TEXT PRIMARY KEY,
            store TEXT,
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

def save_to_db(receipt_id, response):
    conn = sqlite3.connect('receipts.db')
    cursor = conn.cursor()
    
    # レシート情報の保存
    cursor.execute('''
        INSERT INTO receipts (id, store, datetime, total)
        VALUES (?, ?, ?, ?)
    ''', (receipt_id, response['store'], response['datetime'], response['total']))
    
    # 商品情報の保存
    for item in response['items']:
        cursor.execute('''
            INSERT INTO items (receipt_id, name, price)
            VALUES (?, ?, ?)
        ''', (receipt_id, item['name'], item['price']))
    
    conn.commit()
    conn.close()