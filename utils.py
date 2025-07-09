import requests
from langdetect import detect
import os
from dotenv import load_dotenv

load_dotenv()

def download_audio(recording_url):
    resp = requests.get(recording_url + ".mp3")
    return resp.content

def transcribe_with_whisper_api(audio_bytes):
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY_OPENAI')}"
    }
    files = {
        'file': ('audio.mp3', audio_bytes, 'audio/mpeg'),
        'model': (None, 'whisper-1')
    }
    response = requests.post(
        'https://api.openai.com/v1/audio/transcriptions',
        headers=headers,
        files=files
    )
    print("OpenAI API response status:", response.status_code)
    print("OpenAI API response body:", response.text)
    
    response_json = response.json()
    if 'text' not in response_json:
        raise ValueError(f"Missing 'text' in response: {response_json}")
    return response_json['text']


def translate_text(text, target_lang):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        'client': 'gtx',
        'sl': 'auto',
        'tl': target_lang,
        'dt': 't',
        'q': text
    }
    r = requests.get(url, params=params)
    translated_text = r.json()[0][0][0]
    print("Google Translate raw response:", r.text)
    print("Extracted translation:", translated_text)
    return translated_text

def detect_language(text):
    return detect(text)
