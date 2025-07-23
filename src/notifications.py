"""
Notification systems for CPME Monitor.

Handles Pushover, Email, SMS, and WhatsApp notifications.
"""

import logging
import smtplib
from email.message import EmailMessage
from typing import NoReturn

import requests
from twilio.rest import Client as TwilioClient

from .config import (
    PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN,
    GMAIL_EMAIL, GMAIL_PASSWORD, EMAIL_RECIPIENTS,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_SMS, SMS_RECIPIENTS,
    TWILIO_FROM_WHATSAPP, WHATSAPP_RECIPIENTS
)

def send_push(message: str) -> None:
    """Send Pushover notification to iPhone."""
    if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
        logging.warning("Pushover credentials not configured, skipping push notification")
        return

    resp = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": message,
            "title": "🆕 New CPME Listing"
        },
    )
    resp.raise_for_status()

def send_email(subject: str, body: str) -> None:
    """Send email notification to all configured recipients."""
    if not GMAIL_EMAIL or not GMAIL_PASSWORD:
        logging.warning("Gmail credentials not configured, skipping email notification")
        return
    
    if not EMAIL_RECIPIENTS:
        logging.warning("No email recipients configured, skipping email notification")
        return

    for recipient in EMAIL_RECIPIENTS:
        try:
            msg = EmailMessage()
            msg["From"] = GMAIL_EMAIL
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.set_content(body)
            
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(GMAIL_EMAIL, GMAIL_PASSWORD)
                smtp.send_message(msg)
            
            logging.info(f"Email sent successfully to {recipient}")
        except Exception as e:
            logging.error(f"Failed to send email to {recipient}: {e}")

def send_sms(body: str) -> None:
    """Send SMS notification to all configured recipients."""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_SMS]) or "XXX" in (TWILIO_FROM_SMS or ""):
        logging.warning("Twilio SMS credentials not configured, skipping SMS notification")
        return
    
    if not SMS_RECIPIENTS:
        logging.warning("No SMS recipients configured, skipping SMS notification")
        return
    
    client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    for recipient in SMS_RECIPIENTS:
        try:
            client.messages.create(body=body, from_=TWILIO_FROM_SMS, to=recipient)
            logging.info(f"SMS sent successfully to {recipient}")
        except Exception as e:
            logging.error(f"Failed to send SMS to {recipient}: {e}")

def send_whatsapp(body: str) -> None:
    """Send WhatsApp notification to all configured recipients."""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_WHATSAPP]) or "XXX" in (TWILIO_FROM_WHATSAPP or ""):
        logging.warning("Twilio WhatsApp credentials not configured, skipping WhatsApp notification")
        return
    
    if not WHATSAPP_RECIPIENTS:
        logging.warning("No WhatsApp recipients configured, skipping WhatsApp notification")
        return
    
    client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    for recipient in WHATSAPP_RECIPIENTS:
        try:
            client.messages.create(body=body, from_=f"whatsapp:{TWILIO_FROM_WHATSAPP}", to=f"whatsapp:{recipient}")
            logging.info(f"WhatsApp sent successfully to {recipient}")
        except Exception as e:
            logging.error(f"Failed to send WhatsApp to {recipient}: {e}")

def send_all_notifications(message: str) -> None:
    """Send notifications through all configured channels."""
    logging.info("🎉 New listings detected! Sending notifications...")
    
    # Send notifications (each function handles its own error checking)
    try:
        send_push(message)
    except Exception as e:
        logging.error(f"Pushover notification failed: {e}")
    
    try:
        send_email("🆕 New CPME Listing", message)
    except Exception as e:
        logging.error(f"Email notification failed: {e}")
    
    try:
        send_sms(message)
    except Exception as e:
        logging.error(f"SMS notification failed: {e}")
    
    try:
        send_whatsapp(message)
    except Exception as e:
        logging.error(f"WhatsApp notification failed: {e}")