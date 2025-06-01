import logging
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import os
import re

app = Flask(__name__)

# Set up logging to stdout for systemd
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# configure this in your .env file!
US_TWILIO_NUMBER = os.getenv("US_TWILIO_NUMBER")  # e.g., +18123456789
UK_TWILIO_NUMBER = os.getenv("UK_TWILIO_NUMBER")  # e.g., +447123456789
PERSONAL_UK = os.getenv("PERSONAL_UK")            # e.g., +447123456789
PERSONAL_US = os.getenv("PERSONAL_US")            # e.g., +18123456789

# optional SMS when someone is calling you it sends you a text with emojis :)
# env vars
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Initialize Twilio client if credentials are provided
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    twilio_client = None
    logger.warning("🚫 Twilio client not initialized. 🔐 Check your environment variables.")

# ignore this :)
# ENABLE_US_PERSONAL_ROUTING = os.getenv("ENABLE_US_PERSONAL_ROUTING", "false").lower() == "true"

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

# route incoming calls from the US twilio number to the UK twilio number
# it works
@app.route("/voice_us", methods=["POST"])
def voice_us():
    caller = request.form.get("From")
    logger.info(f"📞 Incoming US call from {caller}")

    # send sms with info about the call
    if twilio_client:
        try:
            message = twilio_client.messages.create(
                body=f"📞 Incoming US call from {caller}.",
                from_=UK_TWILIO_NUMBER,
                to=PERSONAL_UK
            )
            logger.info(f"🗨️ SMS sent: {message.sid}")
        except Exception as e:
            logger.error(f"🚫 Failed to send SMS: {e}")

    response = VoiceResponse()
    logger.info(f"🔁 Forwarding US call to UK Phone: {PERSONAL_UK} (Caller ID: {caller})")
    response.dial(PERSONAL_UK, caller_id=caller)
    return Response(str(response), mimetype="application/xml")

# not used at the moment, because it's not been implemented in /voice_us
# if it was going to be used, it would be something like /voice_uk, but with the US bits instead
@app.route("/handle_us_dial", methods=["POST"])
def handle_us_dial():
    logger.warning("🚫 US personal outbound dialing attempted (disabled).")
    response = VoiceResponse()
    response.say("Outbound calling from US is currently disabled.")
    return Response(str(response), mimetype="application/xml")

# handles incoming calls to the UK twilio number
@app.route("/voice_uk", methods=["POST"])
def voice_uk():
    caller = request.form.get("From")
    logger.info(f"📞 Incoming UK call from {caller}")
    response = VoiceResponse()

    # holdup - if the caller is Leo, then allow Leo to dial someone, instead of dialiing himself :)
    if caller == PERSONAL_UK:
        logger.info("🔐 UK personal number - waiting for digits")
        gather = Gather(input="dtmf", finish_on_key="#", action="/handle_uk_dial", method="POST")
        # gather.say("Pact ID ready")
        response.append(gather)
        response.say("We didn't receive any input.")
    else:

        # send sms with info about the call
        if twilio_client:
            try:
                message = twilio_client.messages.create(
                    body=f"📞 Incoming UK call from {caller}.",
                    from_=UK_TWILIO_NUMBER,
                    to=PERSONAL_UK
                )
                logger.info(f"🗨️ SMS sent: {message.sid}")
            except Exception as e:
                logger.error(f"🚫 Failed to send SMS: {e}")

        # otherwise, just forward the call to Leo :)
        logger.info(f"🔁 Forwarding inbound UK Twilio call to UK Personal: {PERSONAL_UK} (Caller ID: {caller})")
        response.dial(PERSONAL_UK, caller_id=caller)

    return Response(str(response), mimetype="application/xml")

# handles dialing out from the UK twilio number to a number entered by Leo (PERSONAL_UK)
@app.route("/handle_uk_dial", methods=["POST"])
def handle_uk_dial():
    digits = request.form.get("Digits")
    response = VoiceResponse()
    if digits:
        to_number = normalize_number(digits)
        logger.info(f"📤 Outbound call from US Twilio to {to_number}")
        response.dial(to_number, caller_id=US_TWILIO_NUMBER)
    else:
        logger.warning("⚠️ No number entered for UK personal outbound dial.")
        response.say("Invalid number.")
    return Response(str(response), mimetype="application/xml")

# this is what betterstack pings to check if it's still alive. so far it has 100% uptime, apart from when I kill it >:)
@app.route("/status", methods=["GET"])
def status():
    return "OK", 200

#redundant
#doesn't actually do sh1t when you're using gunicorn :3
if __name__ == "__main__":
    app.run(debug=False, port=8080)
