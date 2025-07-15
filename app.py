from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from utils import (
    download_audio,
    transcribe_with_whisper_api,
    choose_voice,
    choose_langcode,
    translate_text
)
import traceback

app = Flask(__name__)

user_preferences = {}

@app.route("/", methods=["GET"])
def index():
    return "OK", 200

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    response.say("Welcome. Please say your preferred language after the beep.")
    response.record(
        action="/set_language",
        method="POST",
        max_length=5,
        timeout=3,
        transcribe=False
    )
    return Response(str(response), mimetype="text/xml")

@app.route("/set_language", methods=["POST"])
def set_language():
    response = VoiceResponse()
    call_sid = request.form.get("CallSid")
    try:
        recording_url = request.form["RecordingUrl"]
        audio = download_audio(recording_url)
        lang = transcribe_with_whisper_api(audio)
        print("Detected language:", lang)

        if lang.startswith("english"):
            lang = "spanish"
        user_preferences[call_sid] = lang

        response.say(f"Language set to {lang.capitalize()}. You may begin speaking.")
    except Exception as e:
        traceback.print_exc()
        user_preferences[call_sid] = "spanish"
        response.say("Sorry, I couldn't understand. Defaulting to Spanish. You may begin speaking.")

    response.redirect("/conversation")
    return Response(str(response), mimetype="text/xml")

@app.route("/conversation", methods=["POST"])
def conversation():
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
        call_sid = request.form["CallSid"]
        recording_url = request.form["RecordingUrl"]
        audio = download_audio(recording_url)
        transcript = transcribe_with_whisper_api(audio)
        print("Transcription:", transcript)

        preferred = user_preferences.get(call_sid, "spanish")
        print("Preferred language:", preferred)
        
        translated, target_lang = translate_text(transcript, preferred)
        print(f"Translated to {target_lang}:", translated)

        lang_code = choose_langcode(target_lang)
        voice = choose_voice(target_lang)

        resp = VoiceResponse()
        resp.say(translated, language=lang_code, voice=voice)
        resp.redirect("/conversation")
        return Response(str(resp), mimetype="text/xml")
    except Exception:
        traceback.print_exc()
        resp = VoiceResponse()
        resp.say("Sorry, something went wrong.")
        return Response(str(resp), mimetype="text/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)