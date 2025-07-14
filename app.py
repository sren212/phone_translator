from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from utils import (
    download_audio,
    convert_audio_to_mp3,
    transcribe_with_whisper_api,
    translate_bidirectional,
    text_to_speech_twilio
)
import traceback
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "AI Interpreter is running."

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    response.say("Hello, welcome to the AI interpreter. You may speak after the beep. Press pound when you're done.")
    
    gather = Gather(
        input="speech dtmf",
        timeout=2,
        num_digits=1,
        action="/record_prompt",
        method="POST"
    )
    gather.say("Please speak now.")
    response.append(gather)
    return Response(str(response), mimetype="text/xml")

@app.route("/record_prompt", methods=["POST"])
def record_prompt():
    digit = request.form.get("Digits")
    if digit == "#":
        response = VoiceResponse()
        response.say("Thank you for using the AI interpreter. Goodbye!")
        response.hangup()
        return Response(str(response), mimetype="text/xml")

    # Prompt recording
    response = VoiceResponse()
    response.say("Recording now. Speak after the beep. Press pound when you're done.")
    response.record(
        action="/process_recording",
        method="POST",
        max_length=30,
        finish_on_key="#",
        transcribe=False
    )
    return Response(str(response), mimetype="text/xml")

@app.route("/process_recording", methods=["POST"])
def process_recording():
    try:
        recording_url = request.form["RecordingUrl"]
        audio_bytes = download_audio(recording_url)
        mp3_bytes = convert_audio_to_mp3(audio_bytes)

        transcript = transcribe_with_whisper_api(mp3_bytes)
        print("Transcription:", transcript)

        translated_text, lang = translate_bidirectional(transcript)
        print(f"Detected: {lang}, Translation: {translated_text}")

        twiml_speech = text_to_speech_twilio(translated_text, lang=lang)

        # Replay result, then return to recording prompt
        response = VoiceResponse()
        response.append(twiml_speech)
        response.redirect("/voice")
        return Response(str(response), mimetype="text/xml")

    except Exception as e:
        traceback.print_exc()
        response = VoiceResponse()
        response.say("Sorry, something went wrong.")
        return Response(str(response), mimetype="text/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
