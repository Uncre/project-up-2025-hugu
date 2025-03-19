import gradio as gr
from fastapi import FastAPI
from postimage import main_process
import uvicorn

app = FastAPI()

# gradioインターフェースの定義
def gradio_interface():
    with gr.Blocks() as demo:
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

    return demo

# GradioアプリをFastAPIにマウント
app = gr.mount_gradio_app(app, gradio_interface(), path="/")

# アプリケーション起動処理
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# TODO: excel形式などで出力する
# TODO: Discordとの連携
