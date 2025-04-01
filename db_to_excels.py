import sqlite3
import pandas as pd
from datetime import datetime

def export_database_to_excel(output_path=None):
    """
    SQLiteデータベースからデータを抽出し、Excelファイルに出力する関数
    ISO8601形式の日時データに対応
    
    Args:
        db_path (str): SQLiteデータベースのパス
        output_path (str, optional): 出力するExcelファイルのパス。指定しない場合は現在の日時で自動生成
    
    Returns:
        str: 出力されたExcelファイルのパス
    """

    # データベースのパス
    db_path = "receipts.db"

    # 出力パスが指定されていない場合は現在の日時を使用
    if output_path is None or output_path == "":
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"receipts_data_{current_time}.xlsx"
    
    # データベースに接続
    conn = sqlite3.connect(db_path)
    
    # receiptsテーブルとitemsテーブルのデータを取得
    receipts_df = pd.read_sql_query("SELECT * FROM receipts", conn)
    items_df = pd.read_sql_query("SELECT * FROM items", conn)
    
    # ISO8601形式の日時を適切に処理
    # 表示用に日時のフォーマットを変更（オリジナルデータは保持）
    # 秒がないときの例外処理はISO8601をformatで指定することで対応
    receipts_df['formatted_date'] = pd.to_datetime(receipts_df['datetime'], format='ISO8601').dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # 集計データを作成
    # 店舗ごとの合計金額
    store_summary = receipts_df.groupby('store')['total'].agg(['sum', 'count']).reset_index()
    store_summary.columns = ['店舗', '合計金額', '領収書数']
    
    # ジャンルごとの合計金額
    genre_summary = receipts_df.groupby('genre')['total'].agg(['sum', 'count']).reset_index()
    genre_summary.columns = ['ジャンル', '合計金額', '領収書数']
    
    # 月ごとの合計金額（ISO8601形式から年月を抽出）
    receipts_df['month'] = pd.to_datetime(receipts_df['datetime']).dt.strftime('%Y-%m')
    monthly_summary = receipts_df.groupby('month')['total'].sum().reset_index()
    monthly_summary.columns = ['年月', '合計金額']
    
    # 曜日別の集計も追加
    receipts_df['weekday'] = pd.to_datetime(receipts_df['datetime']).dt.day_name()
    weekday_summary = receipts_df.groupby('weekday')['total'].agg(['sum', 'count']).reset_index()
    weekday_summary.columns = ['曜日', '合計金額', '領収書数']
    
    # Excelファイルに出力
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        # 各データフレームをシートに書き込み
        # レシート一覧シートには整形された日付も含める
        receipts_display = receipts_df.copy()
        receipts_display['datetime_formatted'] = receipts_display['formatted_date']
        receipts_display = receipts_display.drop(columns=['formatted_date', 'month', 'weekday'])
        receipts_display.to_excel(writer, sheet_name='レシート一覧', index=False)
        
        items_df.to_excel(writer, sheet_name='商品詳細', index=False)
        store_summary.to_excel(writer, sheet_name='店舗別集計', index=False)
        genre_summary.to_excel(writer, sheet_name='ジャンル別集計', index=False)
        monthly_summary.to_excel(writer, sheet_name='月別集計', index=False)
        weekday_summary.to_excel(writer, sheet_name='曜日別集計', index=False)
        
        # シート内の列幅を調整
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for i, col in enumerate(writer.sheets[sheet_name].name.split(',')):
                # 各列の最大幅を計算
                if sheet_name == 'レシート一覧':
                    # 日時列は幅を固定
                    if i == receipts_display.columns.get_loc('datetime_formatted') if 'datetime_formatted' in receipts_display.columns else -1:
                        worksheet.set_column(i, i, 20)
                    else:
                        worksheet.set_column(i, i, 15)
                else:
                    worksheet.set_column(i, i, 15)
                    
        # フォーマットの設定
        workbook = writer.book
        money_format = workbook.add_format({'num_format': '¥#,##0'})
        
        # 合計金額列に通貨フォーマットを適用
        for sheet_name in ['店舗別集計', 'ジャンル別集計', '月別集計', '曜日別集計']:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column(1, 1, 15, money_format)  # 合計金額列
    
    conn.close()
    return f"Excelファイルが作成されました: {output_path}"


# if __name__ == "__main__":
#     # 使用例
#     output_file = export_database_to_excel()
#     print(output_file)