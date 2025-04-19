from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import os

app = Flask(__name__)

# configure this in your .env file!
US_TWILIO_NUMBER = os.getenv("US_TWILIO_NUMBER")  # e.g., +18123456789
UK_TWILIO_NUMBER = os.getenv("UK_TWILIO_NUMBER")  # e.g., +447123456789
PERSONAL_UK = os.getenv("PERSONAL_UK")            # e.g., +447123456789
PERSONAL_US = os.getenv("PERSONAL_US")            # e.g., +18123456789
# ignore this :)
ENABLE_US_PERSONAL_ROUTING = os.getenv("ENABLE_US_PERSONAL_ROUTING", "false").lower() == "true"


def normalize_number(raw):
    raw = raw.replace(" ", "")
    if raw.startswith("*"):
        return "+" + raw[1:]
    elif raw.startswith("+"):
        return raw
    elif raw.startswith("07"):
        return "+44" + raw[1:]
    elif raw.startswith("1") and len(raw) == 11:
        return "+" + raw
    return raw

@app.route("/voice_us", methods=["POST"])
def voice_us():
    caller = request.form.get("From")
    response = VoiceResponse()

    if ENABLE_US_PERSONAL_ROUTING and caller == PERSONAL_US:
        gather = Gather(input="dtmf", finish_on_key="#", action="/handle_us_dial", method="POST")
        gather.say("Who do you want to call? Enter the full number, then press hash.")
        response.append(gather)
        response.say("We didn't receive any input.")
    else:
        response.dial(UK_TWILIO_NUMBER, caller_id=caller)

    return Response(str(response), mimetype="application/xml")

@app.route("/handle_us_dial", methods=["POST"])
def handle_us_dial():
    digits = request.form.get("Digits")
    response = VoiceResponse()
    if ENABLE_US_PERSONAL_ROUTING and digits:
        to_number = normalize_number(digits)
        response.dial(to_number, caller_id=PERSONAL_UK)
    else:
        response.say("Outbound calling from US is currently disabled.")
    return Response(str(response), mimetype="application/xml")

@app.route("/voice_uk", methods=["POST"])
def voice_uk():
    caller = request.form.get("From")
    response = VoiceResponse()

    if caller == PERSONAL_UK:
        gather = Gather(input="dtmf", finish_on_key="#", action="/handle_uk_dial", method="POST")
        gather.say("Who do you want to call? Enter the full number, then press hash.")
        response.append(gather)
        response.say("We didn't receive any input.")
    else:
        response.dial(US_TWILIO_NUMBER, caller_id=caller)

    return Response(str(response), mimetype="application/xml")

@app.route("/handle_uk_dial", methods=["POST"])
def handle_uk_dial():
    digits = request.form.get("Digits")
    response = VoiceResponse()
    if digits:
        to_number = normalize_number(digits)
        response.dial(to_number, caller_id=PERSONAL_UK)
    else:
        response.say("Invalid number.")
    return Response(str(response), mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True, port=8080)
