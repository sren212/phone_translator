from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from utils import (
    download_audio,
    transcribe_with_whisper_api,
    detect_language,
    translate_bidirectional
)
import traceback

app = Flask(__name__)
TARGET_LANG = "Spanish"  # default non-English language

@app.route("/", methods=["GET"])
def index():
    return "AI Interpreter is running."

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    response.say("Please speak after the beep.")
    response.record(
        action="/process_recording",
        method="POST",
        max_length=30,
        timeout=2,
        transcribe=False
    )
    return Response(str(response), mimetype="text/xml")

@app.route("/process_recording", methods=["POST"])
def process_recording():
    try:
        recording_url = request.form["RecordingUrl"]
        audio_bytes = download_audio(recording_url)

        transcript = transcribe_with_whisper_api(audio_bytes)
        print("Transcription:", transcript)

        origin_lang = detect_language(transcript)
        print("Detected language:", origin_lang)

        # Translate transcript based on detected language
        if "english" in origin_lang:
            translated_text, lang = translate_bidirectional(transcript, TARGET_LANG)
        else:
            translated_text, lang = translate_bidirectional(transcript, "English")
            TARGET_LANG = origin_lang

        print(f"Translation: {translated_text}")

        # Choose Polly voice
        voice = "Polly.Joanna"
        if lang.lower().startswith("spanish"):
            voice = "Polly.Conchita"
        elif lang.lower().startswith("chinese") or lang.lower().startswith("mandarin"):
            voice = "Polly.Zhiyu"
        elif lang.lower().startswith("korean"):
            voice = "Polly.Seoyeon"
        elif lang.lower().startswith("french"):
            voice = "Polly.Celine"

        response = VoiceResponse()
        response.say(translated_text, language=lang, voice=voice)
        response.redirect("/voice")

        return Response(str(response), mimetype="text/xml")

    except Exception as e:
        traceback.print_exc()
        response = VoiceResponse()
        response.say("Sorry, something went wrong.")
        return Response(str(response), mimetype="text/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)