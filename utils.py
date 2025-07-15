import requests, io, os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def download_audio(url):
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    resp = requests.get(url, auth=(sid, token))
    resp.raise_for_status()
    return resp.content

def transcribe_with_whisper_api(audio):
    resp = openai.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.wav", io.BytesIO(audio), "audio/wav")
    )
    return resp.text

def detect_language(text):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Identify the language of the following sentence."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip().lower()

def translate_text(text, target_lang, origin_lang=None):
    system_prompt = f"Translate this to {target_lang}."
    messages = [{"role":"system","content":system_prompt}]
    if origin_lang:
        messages.append({"role":"system","content":f"Original language: {origin_lang}"})
    messages.append({"role":"user","content":text})
    resp = openai.client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    return resp.choices[0].message.content.strip()

def choose_voice(target_lang):
    t = target_lang.lower()
    return (
        "Polly.Conchita" if t.startswith("spanish") else
        "Polly.Zhiyu" if t.startswith("chinese") else
        "Polly.Seoyeon" if t.startswith("korean") else
        "Polly.Celine" if t.startswith("french") else
        "Polly.Joanna"
    )

def choose_langcode(target_lang):
    t = target_lang.lower()
    if t.startswith("spanish"): return "es-ES"
    if t.startswith("chinese"): return "zh-CN"
    if t.startswith("korean"):  return "ko-KR"
    if t.startswith("french"):  return "fr-FR"
    return "en-US"