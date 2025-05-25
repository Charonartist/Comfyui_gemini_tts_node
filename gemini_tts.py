import os
import json
import base64
import requests
from pathlib import Path

class GeminiTTSNodeFinal:
    """
    Gemini TTS最終修正版
    音声生成が確実に動作するように最適化されたバージョン
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "こんにちは、世界！"}),
                "voice_style": ("STRING", {"multiline": True, "default": "元気で明るい口調で話してください"}),
                "api_key": ("STRING", {"default": ""}),
                "filename": ("STRING", {"default": "output"}),
                "voice": (["Kore", "Puck", "Breeze", "Ember", "Cove"], {"default": "Kore"}),
                "enable_debug": ("BOOLEAN", {"default": True})
            },
            "optional": {
                "output_directory": ("STRING", {"default": "outputs"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("file_path", "status")
    FUNCTION = "generate_speech"
    CATEGORY = "audio/tts"
    
    def generate_speech(self, text, voice_style, api_key, filename, voice, enable_debug=True, output_directory="outputs"):
        """音声を生成するメインメソッド"""
        
        # 初期化とバリデーション
        if not self._validate_inputs(api_key, text, enable_debug):
            return ("", "Error: Invalid inputs")
        
        # 出力ディレクトリの準備
        os.makedirs(output_directory, exist_ok=True)
        
        # プロンプトの構築
        full_prompt = f"{voice_style}\n\n{text}"
        
        if enable_debug:
            print(f"[Gemini TTS] 音声生成開始")
            print(f"[Gemini TTS] テキスト長: {len(text)}文字")
            print(f"[Gemini TTS] 音声: {voice}")
        
        # APIリクエストの実行
        try:
            audio_data, status = self._call_gemini_api(full_prompt, voice, api_key, enable_debug)
            
            if not audio_data:
                return ("", f"Error: {status}")
            
            # ファイル保存
            file_path = self._save_audio_file(audio_data, output_directory, filename, enable_debug)
            
            if file_path:
                success_message = f"Success: Audio saved to {file_path}"
                if enable_debug:
                    print(f"[Gemini TTS] {success_message}")
                return (file_path, success_message)
            else:
                return ("", "Error: Failed to save audio file")
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if enable_debug:
                print(f"[Gemini TTS] {error_msg}")
                import traceback
                traceback.print_exc()
            return ("", error_msg)
    
    def _validate_inputs(self, api_key, text, debug):
        """入力パラメータの検証"""
        if not api_key or api_key.strip() == "":
            if debug:
                print("[Gemini TTS] Error: APIキーが必要です")
            return False
        
        if not text or text.strip() == "":
            if debug:
                print("[Gemini TTS] Error: テキストが必要です")
            return False
        
        return True
    
    def _call_gemini_api(self, prompt, voice, api_key, debug):
        """Gemini APIを呼び出して音声データを取得"""
        
        # API設定
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseModalities": ["AUDIO"]
            },
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice
                    }
                }
            }
        }
        
        if debug:
            print(f"[Gemini TTS] APIリクエスト送信中...")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if debug:
                print(f"[Gemini TTS] レスポンス ステータス: {response.status_code}")
            
            if response.status_code != 200:
                error_detail = response.text[:500] if response.text else "No response body"
                return None, f"API Error {response.status_code}: {error_detail}"
            
            # レスポンス解析
            try:
                response_data = response.json()
                
                if debug:
                    # デバッグ用にレスポンスを保存
                    debug_file = os.path.join("outputs", "last_api_response.json")
                    os.makedirs("outputs", exist_ok=True)
                    with open(debug_file, "w", encoding="utf-8") as f:
                        json.dump(response_data, f, indent=2, ensure_ascii=False)
                    print(f"[Gemini TTS] デバッグ情報を保存: {debug_file}")
                
                # 音声データの抽出
                audio_data = self._extract_audio_from_response(response_data, debug)
                
                if audio_data:
                    return audio_data, "Success"
                else:
                    return None, "No audio data found in response"
                    
            except json.JSONDecodeError as e:
                return None, f"JSON parsing error: {str(e)}"
                
        except requests.RequestException as e:
            return None, f"Request error: {str(e)}"
    
    def _extract_audio_from_response(self, response_data, debug):
        """APIレスポンスから音声データを抽出"""
        
        if debug:
            print("[Gemini TTS] 音声データを検索中...")
        
        # 可能性のあるパスを順次確認
        extraction_paths = [
            # 標準的な構造
            lambda r: r.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("inlineData", {}).get("data"),
            lambda r: r.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("inline_data", {}).get("data"),
            # 代替構造
            lambda r: r.get("candidates", [{}])[0].get("content", {}).get("inlineData", {}).get("data"),
            lambda r: r.get("candidates", [{}])[0].get("content", {}).get("inline_data", {}).get("data"),
            # 直接構造
            lambda r: r.get("audioData"),
            lambda r: r.get("audio", {}).get("data"),
            lambda r: r.get("data")
        ]
        
        for i, extract_func in enumerate(extraction_paths):
            try:
                audio_data = extract_func(response_data)
                if audio_data and isinstance(audio_data, str):
                    if debug:
                        print(f"[Gemini TTS] 音声データを発見 (パターン {i+1})")
                    return audio_data
            except (KeyError, IndexError, TypeError):
                continue
        
        if debug:
            print("[Gemini TTS] 音声データが見つかりませんでした")
            print("[Gemini TTS] レスポンス構造:")
            self._print_structure(response_data, "  ")
        
        return None
    
    def _print_structure(self, obj, indent="", max_depth=3, current_depth=0):
        """レスポンス構造をデバッグ出力"""
        if current_depth >= max_depth:
            return
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    print(f"{indent}{key}: {type(value).__name__}")
                    self._print_structure(value, indent + "  ", max_depth, current_depth + 1)
                else:
                    value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    print(f"{indent}{key}: {value_preview}")
        elif isinstance(obj, list) and obj:
            print(f"{indent}List[{len(obj)}]:")
            self._print_structure(obj[0], indent + "  ", max_depth, current_depth + 1)
    
    def _save_audio_file(self, audio_data, output_dir, filename, debug):
        """Base64音声データをファイルに保存"""
        try:
            # Base64デコード
            audio_bytes = base64.b64decode(audio_data)
            
            if debug:
                print(f"[Gemini TTS] デコード完了: {len(audio_bytes)} bytes")
            
            # ファイル形式の判定
            file_extension = self._detect_audio_format(audio_bytes)
            
            # ファイルパスの生成
            clean_filename = filename.replace('.wav', '').replace('.mp3', '').replace('.ogg', '')
            final_filename = f"{clean_filename}{file_extension}"
            file_path = os.path.join(output_dir, final_filename)
            
            # ファイル保存
            with open(file_path, 'wb') as f:
                f.write(audio_bytes)
            
            if debug:
                print(f"[Gemini TTS] ファイル保存完了: {file_path}")
                print(f"[Gemini TTS] ファイルサイズ: {os.path.getsize(file_path)} bytes")
            
            return file_path
            
        except Exception as e:
            if debug:
                print(f"[Gemini TTS] ファイル保存エラー: {str(e)}")
            return None
    
    def _detect_audio_format(self, audio_bytes):
        """音声データの形式を検出"""
        if len(audio_bytes) < 12:
            return ".wav"  # デフォルト
        
        header = audio_bytes[:12]
        
        # WAV形式
        if header.startswith(b'RIFF') and b'WAVE' in header:
            return ".wav"
        # MP3形式
        elif header.startswith(b'ID3') or header[:2] in [b'\xff\xfb', b'\xff\xfa']:
            return ".mp3"
        # OGG形式
        elif header.startswith(b'OggS'):
            return ".ogg"
        # AAC形式
        elif header[:2] in [b'\xff\xf1', b'\xff\xf9']:
            return ".aac"
        else:
            return ".wav"  # 不明な場合はWAVとして保存


# ノード登録
NODE_CLASS_MAPPINGS = {
    "GeminiTTSFinal": GeminiTTSNodeFinal
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeminiTTSFinal": "🎤 Gemini TTS (最終版)"
}
