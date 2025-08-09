import os

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_number = os.environ["TWILIO_NUMBER"]
client = Client(account_sid, auth_token)


def send_sms(message: str, to_number: str):
    message = client.messages.create(
        body=message,
        from_=twilio_number,
        to=to_number,
    )
    return message.body
