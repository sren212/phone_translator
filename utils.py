import requests
from langdetect import detect
import os
from dotenv import load_dotenv

load_dotenv()

def download_audio(recording_url):
    resp = requests.get(recording_url + ".wav")
    return resp.content

def transcribe_with_whisper_api(audio_bytes):
    headers = {
        "Authorization": f"Bearer {os.getenv("API_KEY_OPENAI")}"
    }
    files = {
        'file': ('audio.wav', audio_bytes, 'audio/wav'),
        'model': (None, 'whisper-1')
    }
    response = requests.post(
        'https://api.openai.com/v1/audio/transcriptions',
        headers=headers,
        files=files
    )
    return response.json()['text']

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
    return translated_text

def detect_language(text):
    return detect(text)
