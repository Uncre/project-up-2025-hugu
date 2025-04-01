import sqlite3
import pandas as pd
from datetime import datetime

def get_receipts_list():
    """
    レシート一覧を二次元配列として取得する関数
    
    Returns:
        list: レシート一覧の二次元配列（ヘッダーなし）
    """
    db_path = "receipts.db"
    conn = sqlite3.connect(db_path)
    receipts_df = pd.read_sql_query("SELECT * FROM receipts", conn)
    
    # ISO8601形式の日時を読みやすい形式に変換
    receipts_df['datetime_formatted'] = pd.to_datetime(receipts_df['datetime'], format='ISO8601').dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # データのみを二次元配列として取得
    result = receipts_df[['id', 'store', 'genre', 'datetime', 'total', 'datetime_formatted']].values.tolist()
    
    conn.close()
    return result

def get_items_detail():
    """
    商品詳細を二次元配列として取得する関数
    
    Returns:
        list: 商品詳細の二次元配列（ヘッダーなし）
    """
    db_path = "receipts.db"
    conn = sqlite3.connect(db_path)
    items_df = pd.read_sql_query("SELECT * FROM items", conn)
    
    # データのみを二次元配列として取得
    result = items_df.values.tolist()
    
    conn.close()
    return result

def get_store_summary():
    """
    店舗別集計を二次元配列として取得する関数
    
    Returns:
        list: 店舗別集計の二次元配列（ヘッダーなし）
    """
    db_path = "receipts.db"
    conn = sqlite3.connect(db_path)
    receipts_df = pd.read_sql_query("SELECT * FROM receipts", conn)
    
    # 店舗ごとの合計金額と件数を集計
    store_summary = receipts_df.groupby('store')['total'].agg(['sum', 'count']).reset_index()
    
    # データのみを二次元配列として取得
    result = store_summary.values.tolist()
    
    conn.close()
    return result

def get_genre_summary():
    """
    ジャンル別集計を二次元配列として取得する関数
    
    Returns:
        list: ジャンル別集計の二次元配列（ヘッダーなし）
    """
    db_path = "receipts.db"
    conn = sqlite3.connect(db_path)
    receipts_df = pd.read_sql_query("SELECT * FROM receipts", conn)
    
    # ジャンルごとの合計金額と件数を集計
    genre_summary = receipts_df.groupby('genre')['total'].agg(['sum', 'count']).reset_index()
    
    # データのみを二次元配列として取得
    result = genre_summary.values.tolist()
    
    conn.close()
    return result

def get_monthly_summary():
    """
    月別集計を二次元配列として取得する関数
    
    Returns:
        list: 月別集計の二次元配列（ヘッダーなし）
    """
    db_path = "receipts.db"
    conn = sqlite3.connect(db_path)
    receipts_df = pd.read_sql_query("SELECT * FROM receipts", conn)
    
    # ISO8601形式の日時から年月を抽出
    receipts_df['month'] = pd.to_datetime(receipts_df['datetime'], format='ISO8601').dt.strftime('%Y-%m')
    
    # 月ごとの合計金額を集計
    monthly_summary = receipts_df.groupby('month')['total'].sum().reset_index()
    
    # データのみを二次元配列として取得
    result = monthly_summary.values.tolist()
    
    conn.close()
    return result

def export_all_data():
    """
    すべてのデータを取得し、辞書形式で返す関数
    
    Returns:
        dict: 各シートのデータを二次元配列で格納した辞書
    """
    return {
        'レシート一覧': get_receipts_list(),
        '商品詳細': get_items_detail(),
        '店舗別集計': get_store_summary(),
        'ジャンル別集計': get_genre_summary(),
        '月別集計': get_monthly_summary()
    }

# if __name__ == "__main__":
#     # 使用例
#     receipts_data = get_receipts_list()
#     items_data = get_items_detail()
#     store_data = get_store_summary()
#     genre_data = get_genre_summary()
#     monthly_data = get_monthly_summary()
    
#     # すべてのデータをまとめて取得
#     all_data = export_all_data()
    
#     # 例: レシート一覧の最初の3行を表示
#     for row in receipts_data[:3]:
#         print(row)