from twilio.rest import Client
import os
from ecommerce_mini.settings import env


def sent_otp(mobile):
    phone = "+91" + str(mobile)
    account_sid = env("TWILIO_ACCOUNT_SID")
    auth_token = env("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)
    verification = client.verify.services(
        env("TWILIO_VERIFY_SERVICE_SID")
    ).verifications.create(to=phone, channel="sms")
    print(verification.status)


def check_otp(mobile, otp):
    account_sid = env("TWILIO_ACCOUNT_SID")
    auth_token = env("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    verification_check = client.verify.services(
        env("TWILIO_VERIFY_SERVICE_SID")
    ).verification_checks.create(to="+91" + mobile, code=otp)

    print(verification_check.status)
    if verification_check.status == "approved":
        return True
    else:
        return False
