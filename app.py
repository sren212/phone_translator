from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from utils import download_audio, transcribe_with_whisper_api, translate_text, detect_language, convert_audio_to_mp3
import os
import traceback

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "AI Interpreter app is running!"

@app.route("/voice", methods=['POST'])
def voice():
    response = VoiceResponse()
    response.say("Welcome to the AI interpreter. Please begin speaking after the beep.")
    response.record(
        action="/process_recording",
        max_length=8,
        play_beep=True,
        timeout=1,
        transcribe=False
    )
    return Response(str(response), mimetype="text/xml")

@app.route("/process_recording", methods=['POST'])
def process_recording():
    recording_url = request.form['RecordingUrl']
    print(f"Received recording URL: {recording_url}")
    
    try:
        audio_bytes_raw = download_audio(recording_url)
        audio_bytes_clean = convert_audio_to_mp3(audio_bytes_raw)
        transcript = transcribe_with_whisper_api(audio_bytes_clean)
    except Exception as e:
        print("Whisper transcription error:")
        traceback.print_exc()
        response = VoiceResponse()
        response.say("Sorry, I could not understand you.")
        response.redirect("/voice")
        return Response(str(response), mimetype="text/xml")

    lang = detect_language(transcript)
    print(f"Detected language: {lang}")
    print(f"Original transcript: '{transcript}'")

    if lang.startswith("en"):
        target_lang = "es"
        tts_lang = "es-ES"
    elif lang.startswith("es"):
        target_lang = "en"
        tts_lang = "en-US"
    else:
        target_lang = "es"
        tts_lang = "es-ES"

    translated_text = translate_text(transcript, target_lang)
    print(f"Translated text: '{translated_text}'")

    response = VoiceResponse()
    response.say(translated_text, language=tts_lang)
    response.redirect("/voice")
    return Response(str(response), mimetype="text/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))