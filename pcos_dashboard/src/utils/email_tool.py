import smtplib
import ssl
from email.message import EmailMessage
import os
import streamlit as st

def send_otp_email(receiver_email, otp_code, username="User"):
    # 1. Fetch credentials from .env
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Error: SENDER_EMAIL or SENDER_PASSWORD is not set in the .env file.")
        return False

    # 2. Create the Email Message
    msg = EmailMessage()
    msg['Subject'] = "PCOS Dashboard - Verification Code"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    
    msg.set_content(f"""
    Hello {username},

    We received a request to verify your identity for access to your PCOS Dashboard account.

    Your one-time verification code is: {otp_code}

    Please enter this code in the app to proceed. For security reasons, this code will expire shortly.

    If you did not request this verification, you may safely ignore this email.

    Thank you,
    PCOS Dashboard Team
    """)

    # 3. Send the Email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"SMTP Error: {e}") 
        return False