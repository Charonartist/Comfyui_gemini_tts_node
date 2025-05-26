まだ動きません

# ComfyUI用Gemini TTS カスタムノード

## 概要
このカスタムノードは、Gemini 2.5 Flash Preview TTS APIを使用して、テキストから音声を生成するためのComfyUI用ノードです。

## 特徴
- words_prompt（セリフ）とsystem_prompt（口調）を入力として受け付けます
- Gemini TTS APIを使用して高品質な音声を生成します
- 複数の音声タイプから選択可能です
- 出力ディレクトリとファイル名をカスタマイズできます

## インストール方法
1. ComfyUIのインストールディレクトリ内の`custom_nodes`フォルダに`gemini_tts_node`フォルダをコピーします
2. ComfyUIを再起動します

## 使用方法
1. ComfyUIのノードブラウザから「Gemini TTS Generator」を追加します
2. 必要なパラメータを設定します：
   - words_prompt: 音声に変換したいテキスト（セリフ）
   - system_prompt: 音声の口調や感情を指定するプロンプト
   - api_key: Gemini APIキー（Google AI Studioから取得）
   - output_filename: 出力ファイル名（.wavは自動追加）
   - voice_name: 使用する音声タイプ（Kore、Puck、Breeze、Ember、Cove）
   - output_dir: 音声ファイルの出力先ディレクトリ（オプション）
3. ワークフローを実行すると、指定したディレクトリに音声ファイルが生成されます

## 注意事項
- このノードを使用するには、有効なGemini APIキーが必要です
- APIキーは個人情報として扱い、公開しないようにしてください
- 生成された音声ファイルは、指定したoutput_dirに保存されます（デフォルトは「outputs」）

## トラブルシューティング
- APIキーが無効な場合はエラーメッセージが表示されます
- ネットワーク接続に問題がある場合は、エラーメッセージを確認してください
- 出力ディレクトリが存在しない場合は自動的に作成されます

## ライセンス
このカスタムノードは自由に使用・改変・再配布可能です。
