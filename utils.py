import requests
from pydub import AudioSegment
import io
import openai
import os
from twilio.rest import Client

openai.api_key = os.getenv("OPENAI_API_KEY")

def download_audio(recording_url):
    resp = requests.get(recording_url + ".wav")
    resp.raise_for_status()
    return resp.content

def convert_audio_to_mp3(wav_bytes):
    audio = AudioSegment.from_wav(io.BytesIO(wav_bytes))
    buffer = io.BytesIO()
    audio.export(buffer, format="mp3")
    return buffer.getvalue()

def transcribe_with_whisper_api(audio_mp3_bytes):
    response = openai.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.mp3", io.BytesIO(audio_mp3_bytes), "audio/mpeg")
    )
    return response.text

def translate_text(text, target_lang="es"):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Translate the following English text to {target_lang}."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

def text_to_speech_twilio(text):
    # Create a TwiML Bin-like URL by generating a TwiML file
    response = VoiceResponse()
    response.say(text, voice="Polly.Conchita")  # Use a Spanish voice or change language
    twiml = str(response)

    # Upload TwiML to a temporary server or prehost translated messages
    # Here we simulate using Twilio’s <Say>, you can also pre-generate audio and host it
    return f"https://handler.twilio.com/twiml/EHXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX?Body={text}"