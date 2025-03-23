import tempfile
import discord
from postimage import main_process
import json

# 設定ファイルの読み込み
with open("config.json", 'r') as config_file:
    config = json.load(config_file)
# discordボットのトークン
TOKEN = config("discord_bot_token")
# 接続するチャンネルID
CHANNEL_ID = config("discord_channel_id")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    # ログインしたらターミナルにログイン通知が表示される
    print("ログインしました")
    channel = client.get_channel(CHANNEL_ID)
    await channel.send('botが起動しました')

@client.event
async def on_message(message):
    # bot自身のメッセージは無視する
    if message.author == client.user:
        return

    # チャンネルIDが一致しているか
    if message.channel.id == CHANNEL_ID:
        # メッセージがアタッチメントを持っているか
        if len(message.attachments) > 0:
            for index, attachment in enumerate(message.attachments, start=1):
                # 画像の場合
                if attachment.content_type.startswith("image"):
                    # 画像のdl
                    image_data = await attachment.read()

                    # 一時ファイルに保存
                    with tempfile.NamedTemporaryFile(delete=True) as tf:
                        tf.write(image_data)
                        image_path = tf.name
                        # 画像をAIに投げて結果を取得
                        response = main_process(image_path, is_discord=True)
                        # 結果をチャンネルに送信
                        await message.channel.send(response)
                        # withブロックを抜けると一時ファイルは削除される

# 動作未確認！！！！テストしろ
# client.run(TOKEN)

