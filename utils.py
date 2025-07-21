import requests, io, os, time
from twilio.rest import Client
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# downloads audio and then deletes it
def download_audio(url):
    if not url.endswith('.wav'):
        url += '.wav'
    
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    recording_sid = url.split("/")[-1].replace(".wav", "")

    for i in range(3):
        try:
            resp = requests.get(url, auth=(sid, token))
            resp.raise_for_status()
            
            try:
                twilio_client.recordings(recording_sid).delete()
            except Exception as e:
                print(f"Warning: Failed to delete recording {recording_sid}: {e}")
            
            return resp.content
        except Exception as e:
            if i == 2:
                raise e
            time.sleep(1)

def transcribe_with_whisper_api(audio):
    resp = client.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.wav", io.BytesIO(audio), "audio/wav")
    )
    return resp.text

def detect_language(text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "In English, identify the language of the following sentence in exactly one word."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip().lower()

def translate_text(text, preferred):
    system_prompt = f"You are an interpreter for an english-speaking and a {preferred}-speaking person in a clinic setting. Translate this message and provide only the translation in your response."
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )
    translated = resp.choices[0].message.content.strip()
    return translated, detect_language(translated)

def choose_voice(target_lang):
    t = target_lang.lower()
    return (
        "Polly.Conchita" if t.startswith("spanish") else
        "Polly.Zhiyu" if t.startswith("chinese") else
        "Polly.Hiujin" if t.startswith("cantonese") else
        "Polly.Seoyeon" if t.startswith("korean") else
        "Polly.Celine" if t.startswith("french") else
        "Polly.Aditi" if t.startswith("hindi") else
        "Polly.Zeina" if t.startswith("arabic") else
        "Polly.Joanna"
    )

def choose_langcode(target_lang):
    t = target_lang.lower()
    return (
        "es-ES" if t.startswith("spanish") else
        "zh-CN" if t.startswith("chinese") else
        "yue-CN" if t.startswith("cantonese") else
        "ko-KR" if t.startswith("korean") else
        "fr-FR" if t.startswith("french") else
        "hi-IN" if t.startswith("hindi") else
        "arb" if t.startswith("arabic") else
        "en-US"
    )