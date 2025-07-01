from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from utils import download_audio, transcribe_with_whisper_api, translate_text, detect_language
import os

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
    audio_data = download_audio(recording_url)

    try:
        transcript = transcribe_with_whisper_api(audio_data)
    except Exception as e:
        response = VoiceResponse()
        response.say("Sorry, I could not understand you.")
        response.redirect("/voice")
        return Response(str(response), mimetype="text/xml")

    lang = detect_language(transcript)

    if lang.startswith("en"):
        target_lang = "es"
        tts_lang = "es-ES"
    elif lang.startswith("es"):
        target_lang = "en"
        tts_lang = "en-US"
    else:
        # Default to Spanish if unknown
        target_lang = "es"
        tts_lang = "es-ES"

    translated_text = translate_text(transcript, target_lang)

    response = VoiceResponse()
    response.say(translated_text, language=tts_lang)
    response.redirect("/voice")
    return Response(str(response), mimetype="text/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
