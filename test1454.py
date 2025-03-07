import os
import json
import sqlite3
import uuid
from datetime import datetime
from PIL import Image
import google.generativeai as genai

class ReceiptManager:
    def __init__(self, gemini_api_key, db_path):
        # Gemini APIの設定
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        
        # SQLiteデータベースの初期設定
        self.db_path = db_path
        self._setup_database()
    
    def _setup_database(self):
        """データベースの初期設定"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # レシート一覧テーブルの作成
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id TEXT PRIMARY KEY,
            date TEXT,
            time TEXT,
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
    
    def process_receipt(self, image_path):
        """レシート画像の処理メインフロー"""
        # 画像の読み込み
        image = Image.open(image_path)
        
        # Gemini APIによる画像分析
        response = self._analyze_with_gemini(image)
        
        # レシートIDの生成
        receipt_id = str(uuid.uuid4())
        
        # データベースへの保存
        self._save_to_database(receipt_id, response)
        
        return receipt_id, response
    
    def _analyze_with_gemini(self, image):
        """Gemini APIを使用してレシート画像を分析"""
        # プロンプトの設定
        prompt = """
        このレシートを分析し、以下の形式でJSONを返してください：
        {
            "date": "YYYY/MM/DD",
            "time": "HH:MM",
            "total": 合計金額,
            "items": [
                {"name": "商品名", "price": 金額},
                ...
            ]
        }
        """
        
        # API呼び出し
        response = self.model.generate_content([prompt, image])
        
        # レスポンスからJSONを抽出して解析
        try:
            json_str = response.text.strip('```json\n').strip('```')
            return json.loads(json_str)
        except json.JSONDecodeError:
            raise Exception("Gemini APIからの応答をJSONとして解析できませんでした。")
    
    def _save_to_database(self, receipt_id, data):
        """SQLiteデータベースにデータを保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # レシート情報を保存
            cursor.execute(
                "INSERT INTO receipts (id, date, time, total) VALUES (?, ?, ?, ?)",
                (receipt_id, data['date'], data['time'], data['total'])
            )
            
            # 商品情報を保存
            for item in data['items']:
                cursor.execute(
                    "INSERT INTO items (receipt_id, name, price) VALUES (?, ?, ?)",
                    (receipt_id, item['name'], item['price'])
                )
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def process_json_response(self, json_response):
        """Gemini APIのJSONレスポンスを直接処理する"""
        # レシートIDの生成
        receipt_id = str(uuid.uuid4())
        
        # データベースへの保存
        self._save_to_database(receipt_id, json_response)
        
        return receipt_id

    def get_receipt(self, receipt_id):
        """レシート情報の取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # レシート基本情報の取得
        cursor.execute("SELECT * FROM receipts WHERE id = ?", (receipt_id,))
        receipt = cursor.fetchone()
        
        if not receipt:
            conn.close()
            return None
        
        # 商品情報の取得
        cursor.execute("SELECT name, price FROM items WHERE receipt_id = ?", (receipt_id,))
        items = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # 結果の整形
        result = dict(receipt)
        result['items'] = items
        
        return result

# 使用例
if __name__ == "__main__":
    # 設定
    GEMINI_API_KEY = "your_api_key_here"
    DB_PATH = "receipts.db"
    
    # レシートマネージャーの初期化
    manager = ReceiptManager(GEMINI_API_KEY, DB_PATH)
    
    # Geminiからのレスポンス例
    gemini_response = {
        "date": "2022/01/01",
        "time": "12:34", 
        "total": 1000,
        "items": [
            {"name": "item1", "price": 500},
            {"name": "item2", "price": 500}
        ]
    }
    
    # JSONレスポンスの処理
    receipt_id = manager.process_json_response(gemini_response)
    print(f"処理完了 - レシートID: {receipt_id}")
    
    # 保存したデータの取得・確認
    saved_receipt = manager.get_receipt(receipt_id)
    print(f"保存されたデータ: {json.dumps(saved_receipt, indent=2, ensure_ascii=False)}")
    
    # 画像から直接処理する場合のコード例
    # receipt_id, response = manager.process_receipt("path_to_receipt_image.jpg")