# Receipt Kanri
AIを用いてレシートをスマートに管理するアプリ

## 機能
### WebUI
写真を送信してレシートを解析
データベースの閲覧
Excelへの出力

### Discord Bot
写真をチャンネルに投稿でレシートを解析

## 特長
### AIを用いた解析
・Googleが提供するGemini AIを利用するため、高精度に分析が可能
・手書きや複雑な構造のレシートにも対応 
・AIがレシートの内容から自動的にジャンル分け

### Discordとの連携
Discordからいつでもどこでも写真を解析可能

## 準備
requirements.txtをインストール
geminiのAPIキー(環境変数GEMINI_API_KEYに登録しておくと使いやすくなります)
Discordのbotトークン、チャンネルID（config.jsonに記載してください）
