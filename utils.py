import requests
import io
import openai
import os
from twilio.rest import Client
import subprocess
import tempfile

openai.api_key = os.getenv("OPENAI_API_KEY")

def download_audio(recording_url):
    resp = requests.get(recording_url + ".wav")
    resp.raise_for_status()
    return resp.content

def convert_audio_to_mp3(wav_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
        wav_file.write(wav_bytes)
        wav_file_path = wav_file.name

    mp3_file_path = wav_file_path.replace(".wav", ".mp3")

    subprocess.run([
        "ffmpeg", "-y",
        "-i", wav_file_path,
        mp3_file_path
    ], check=True)

    with open(mp3_file_path, "rb") as f:
        mp3_data = f.read()

    os.remove(wav_file_path)
    os.remove(mp3_file_path)

    return mp3_data

def transcribe_with_whisper_api(audio_mp3_bytes):
    response = openai.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.mp3", io.BytesIO(audio_mp3_bytes), "audio/mpeg")
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

def translate_bidirectional(text):
    lang = detect_language(text)
    if "spanish" in lang:
        target_lang = "English"
    elif "english" in lang:
        target_lang = "Spanish"
    else:
        target_lang = "English"  # default fallback

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Translate this to {target_lang}."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip(), target_lang

def text_to_speech_twilio(text, lang="Spanish"):
    # Select Twilio-compatible voices
    if lang.lower().startswith("spanish"):
        voice = "Polly.Conchita"
    else:
        voice = "Polly.Joanna"

    response = VoiceResponse()
    response.say(text, voice=voice)
    return str(response)