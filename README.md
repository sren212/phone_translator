# AI Phone Interpreter

This project provides a low-cost, HIPAA-ready phone interpreter designed for **front desk staff at CCACC Health Clinic**, a nonprofit medical clinic serving primarily immigrant and uninsured patients in Gaithersburg, Maryland.

The interpreter enables staff to **communicate with patients in their preferred language over the phone**, without relying on a human translator. Common use cases include:
- Scheduling or confirming appointments  
- Communicating test results  
- Answering patient questions  

---

## How It Works

1. **Incoming call**: A patient calls the clinic or arrives at the clinic. The interpreter phone number is connected to the call or called in-person.
2. **Recording**: The call is recorded through [Twilio](https://www.twilio.com/).
3. **Transcription**: The audio is transcribed using [OpenAI Whisper](https://platform.openai.com/docs/guides/speech-to-text/whisper).
4. **Translation**: The transcription is translated to the other party’s language using [OpenAI GPT-4](https://platform.openai.com/docs/guides/gpt).
5. **Text-to-Speech (TTS)**: The translated text is spoken aloud using [Twilio Text to Speech](https://www.twilio.com/docs/voice/twiml/say/text-speech).
6. **Secure Deletion**: Recordings are deleted from Twilio after transcription to ensure zero data retention.

---

## HIPAA Compliance

This project is being developed with HIPAA compliance in mind. Key protections include:

- **End-to-end encryption (HTTPS)** for all API calls  
- **No data retention** in OpenAI (will be ensured via Business Associate Agreement)  
- **Immediate deletion** of Twilio recordings after processing  
- **Hosting on [Microsoft Azure App Service](https://azure.microsoft.com/en-us/products/app-service/)**, with secure environment variable storage  
- **BAAs being requested** from OpenAI, Twilio, and Microsoft Azure  

---

## Technologies Used

- [OpenAI Whisper](https://platform.openai.com/docs/guides/speech-to-text/whisper) — Speech-to-text  
- [OpenAI GPT-4](https://platform.openai.com/docs/guides/gpt) — Translation  
- [Twilio Voice](https://www.twilio.com/voice) — Phone call routing and recording, text-to-speech
- [Flask](https://flask.palletsprojects.com/) — Backend server  
- [Azure App Service](https://azure.microsoft.com/en-us/products/app-service/) — Deployment  

---

## Deployment

The app is deployed to Azure.

https://phoneinterpreter-g3bsd5a6fhazebhq.canadacentral-01.azurewebsites.net/
