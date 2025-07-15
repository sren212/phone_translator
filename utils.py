import requests
import io
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def download_audio(recording_url):
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    print(f"Downloading from: {recording_url}")
    resp = requests.get(recording_url, auth=(twilio_sid, twilio_token))
    resp.raise_for_status()
    return resp.content

def transcribe_with_whisper_api(audio):
    response = openai.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.wav", io.BytesIO(audio), "audio/wav")
    )
    return response.text

def detect_language(text):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Identify the language of the following sentence."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip().lower()

def translate_bidirectional(text, target_lang):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Translate this to {target_lang}."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip(), target_lang