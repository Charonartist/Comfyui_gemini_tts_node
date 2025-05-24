import os
import json
import wave
import base64
import requests
from pathlib import Path

class GeminiTTSNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "words_prompt": ("STRING", {"multiline": True, "default": "こんにちは、世界！"}),
                "system_prompt": ("STRING", {"multiline": True, "default": "元気で明るい口調"}),
                "api_key": ("STRING", {"default": ""}),
                "output_filename": ("STRING", {"default": "gemini_tts_output.wav"}),
                "voice_name": (["Kore", "Puck", "Breeze", "Ember", "Cove"], {"default": "Kore"}),
            },
            "optional": {
                "output_dir": ("STRING", {"default": "outputs"})
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("audio_path",)
    FUNCTION = "generate_tts"
    CATEGORY = "audio/tts"
    
    def generate_tts(self, words_prompt, system_prompt, api_key, output_filename, voice_name, output_dir="outputs"):
        # 出力ディレクトリの作成
        os.makedirs(output_dir, exist_ok=True)
        
        # 出力ファイルパスの設定
        if not output_filename.endswith('.wav'):
            output_filename += '.wav'
        output_path = os.path.join(output_dir, output_filename)
        
        # APIキーのチェック
        if not api_key:
            print("Error: API key is required")
            return (f"Error: API key is required",)
        
        try:
            # Gemini TTS APIリクエストの構築
            # system_promptとwords_promptを組み合わせてプロンプトを作成
            prompt = f"{system_prompt}: {words_prompt}"
            
            # APIリクエストの設定
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key
            }
            
            # リクエストボディの構築
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generation_config": {
                    "response_modalities": ["AUDIO"]
                },
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": voice_name
                        }
                    }
                }
            }
            
            # APIリクエストの送信
            response = requests.post(url, headers=headers, json=data)
            
            # レスポンスの処理
            if response.status_code == 200:
                response_json = response.json()
                
                # 音声データの取得
                audio_data = response_json["candidates"][0]["content"]["parts"][0]["inline_data"]["data"]
                audio_bytes = base64.b64decode(audio_data)
                
                # WAVファイルとして保存
                with wave.open(output_path, "wb") as wf:
                    wf.setnchannels(1)  # モノラル
                    wf.setsampwidth(2)  # 16ビット
                    wf.setframerate(24000)  # サンプリングレート
                    wf.writeframes(audio_bytes)
                
                print(f"Audio saved to {output_path}")
                return (output_path,)
            else:
                error_message = f"API Error: {response.status_code} - {response.text}"
                print(error_message)
                return (error_message,)
                
        except Exception as e:
            error_message = f"Error: {str(e)}"
            print(error_message)
            return (error_message,)

# ノードの登録
NODE_CLASS_MAPPINGS = {
    "GeminiTTS": GeminiTTSNode
}

# 表示名の設定
NODE_DISPLAY_NAME_MAPPINGS = {
    "GeminiTTS": "Gemini TTS Generator"
}
