import gradio as gr
from fastapi import FastAPI
from postimage import main_process
from db_to_excels import export_database_to_excel
import db_to_list as dbl
import uvicorn

app = FastAPI()

# gradioインターフェースの定義
def gradio_interface():
    with gr.Blocks() as demo:
        with gr.Tab("レシート登録"):
            gr.Markdown("# Receipt Kanri")
            gr.Markdown("## API Key")
            gr.Markdown("入力が空の場合は環境変数（GEMINI_API_KEY）から取得します")
            text_box_apikey = gr.Textbox(lines=1, label="Your API Key")

            gr.Markdown("## Image")
            gr.Markdown("入力が空の場合はimagesフォルダ内の画像を使用します")
            image_folder_path = gr.Textbox(lines=1, label="Image Folder Path")
            run_btn = gr.Button("Run")

            gr.Markdown("## Output")
            output = gr.Textbox(lines=10, label="Output")

            run_btn.click(fn=main_process,
                        inputs=(image_folder_path, text_box_apikey),
                        outputs=output
                        )
            
            
        with gr.Tab("データベース表示"):
            with gr.Tab("概要"):
                gr.Markdown("# データベース表示")
                gr.Markdown("このタブでは、レシートの分析が可能です。各タブを選択して詳細データを表示します。")

            with gr.Tab("レシート一覧") as tab_receipts_list:
                df_receipts_list = gr.Dataframe(headers=['ID', '店舗', 'ジャンル', '日時(ISO8601)', '合計金額', '日時(表示用)'], show_search="filter", interactive=False)
                tab_receipts_list.select(fn=dbl.get_receipts_list, outputs=df_receipts_list)

            with gr.Tab("商品詳細") as tab_items_detail:
                df_items_detail = gr.Dataframe(headers=['ID', 'レシートID', '商品名', '価格'], show_search="filter", interactive=False)
                tab_items_detail.select(fn=dbl.get_items_detail, outputs=df_items_detail)

            with gr.Tab("店舗別集計") as tab_store_summary:
                df_store_summary = gr.Dataframe(headers=['店舗', '合計金額', '領収書数'], show_search="filter", interactive=False)
                tab_store_summary.select(fn=dbl.get_store_summary, outputs=df_store_summary)
            
            with gr.Tab("ジャンル別集計") as tab_genre_summary:
                df_genre_summary = gr.Dataframe(headers=['ジャンル', '合計金額', '領収書数'], show_search="filter", interactive=False)
                tab_genre_summary.select(fn=dbl.get_genre_summary, outputs=df_genre_summary)

            with gr.Tab("月別集計") as tab_monthly_summary:
                df_monthly_summary = gr.Dataframe(headers=['年月', '合計金額'], show_search="filter", interactive=False)
                tab_monthly_summary.select(fn=dbl.get_monthly_summary, outputs=df_monthly_summary)


        with gr.Tab("Excel出力"): 
            gr.Markdown("## Excelに出力")
            gr.Markdown("データベースをExcelに出力します")
            gr.Markdown("### 出力先")
            gr.Markdown("入力が空の場合は、receipts_data_{現在日時}.xlsx として出力します")
            excel_output_path = gr.Textbox(lines=1, label=" Excel Output Path")
            excel_btn = gr.Button("Export")
            excel_result = gr.Textbox(lines=1, label="Result")

            excel_btn.click(fn=export_database_to_excel,
                            inputs=excel_output_path,
                            outputs=excel_result
                        )

    return demo

# GradioアプリをFastAPIにマウント
app = gr.mount_gradio_app(app, gradio_interface(), path="/")

# アプリケーション起動処理
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# TODO: excel形式などで出力する ←OK
# TODO: Discordとの連携
# TODO: DBの内容をCSVに出力、html形式でwebuiに表示　(CSV経由しなくてもよくね？)
# →gradioでdataframeを表示する方法があるので、それを使う OK
# TODO: 検索機能の拡充（IDによる商品詳細の絞りこみなど）
