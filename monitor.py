import json
import logging
import os
import requests
import signal
import smtplib
import sys
import threading
import time

from dotenv import load_dotenv
from email.message import EmailMessage
from pathlib import Path
from playwright.sync_api import sync_playwright
from twilio.rest import Client as TwilioClient

# ——— Load configuration ———
load_dotenv(override=True)  # Force reload environment variables

PUSH_USER    = os.getenv("PUSHOVER_USER_KEY")
PUSH_TOKEN   = os.getenv("PUSHOVER_API_TOKEN")
GMAIL_EMAIL  = os.getenv("GMAIL_EMAIL")
GMAIL_PASS   = os.getenv("GMAIL_PASSWORD")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "").split(",") if os.getenv("EMAIL_RECIPIENTS") else []
TW_SID       = os.getenv("TWILIO_ACCOUNT_SID")
TW_TOKEN     = os.getenv("TWILIO_AUTH_TOKEN")
TW_FROM_SMS  = os.getenv("TWILIO_FROM_SMS")
SMS_RECIPIENTS = os.getenv("SMS_RECIPIENTS", "").split(",") if os.getenv("SMS_RECIPIENTS") else []
TW_FROM_WA   = os.getenv("TWILIO_FROM_WHATSAPP")
WA_RECIPIENTS = os.getenv("WHATSAPP_RECIPIENTS", "").split(",") if os.getenv("WHATSAPP_RECIPIENTS") else []

LAST_COUNT_FILE = Path(os.getenv("LAST_COUNT_FILE", "last_count.txt"))
POLL_INTERVAL   = int(os.getenv("POLL_INTERVAL", "30"))  # seconds

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    global shutdown_requested
    logging.info("Shutdown signal received. Finishing current check...")
    shutdown_requested = True

# ——— Helpers ———
def fetch_habitacional_count():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://cpme.fyidigital.pt/arrendamento")
        page.wait_for_load_state("networkidle")
        # grab all "Andares disponíveis: X"
        counts = page.evaluate("""
            Array.from(document.querySelectorAll('*'))
                .map(el => el.textContent.trim())
                .filter(text => text.startsWith('Andares disponíveis'))
                .map(text => parseInt(text.match(/\\d+/)[0]));
        """)
        browser.close()
        return counts[0] if counts else 0

def send_push(message):
    if not PUSH_USER or not PUSH_TOKEN:
        logging.warning("Pushover credentials not configured, skipping push notification")
        return

    resp = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": PUSH_TOKEN,
            "user": PUSH_USER,
            "message": message,
            "title": "🆕 New Habitacional Listing"
        },
    )
    resp.raise_for_status()

def send_email(subject, body):
    if not GMAIL_EMAIL or not GMAIL_PASS:
        logging.warning("Gmail credentials not configured, skipping email notification")
        return
    
    if not EMAIL_RECIPIENTS:
        logging.warning("No email recipients configured, skipping email notification")
        return

    # Clean up email addresses (strip whitespace)
    recipients = [email.strip() for email in EMAIL_RECIPIENTS if email.strip()]
    
    for recipient in recipients:
        try:
            msg = EmailMessage()
            msg["From"]    = GMAIL_EMAIL
            msg["To"]      = recipient
            msg["Subject"] = subject
            msg.set_content(body)
            
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(GMAIL_EMAIL, GMAIL_PASS)
                smtp.send_message(msg)
            
            logging.info(f"Email sent successfully to {recipient}")
        except Exception as e:
            logging.error(f"Failed to send email to {recipient}: {e}")

def send_sms(body):
    if not all([TW_SID, TW_TOKEN, TW_FROM_SMS]) or "XXX" in (TW_FROM_SMS or ""):
        logging.warning("Twilio SMS credentials not configured, skipping SMS notification")
        return
    
    if not SMS_RECIPIENTS:
        logging.warning("No SMS recipients configured, skipping SMS notification")
        return

    # Clean up phone numbers (strip whitespace)
    recipients = [phone.strip() for phone in SMS_RECIPIENTS if phone.strip()]
    
    client = TwilioClient(TW_SID, TW_TOKEN)
    
    for recipient in recipients:
        try:
            client.messages.create(body=body, from_=TW_FROM_SMS, to=recipient)
            logging.info(f"SMS sent successfully to {recipient}")
        except Exception as e:
            logging.error(f"Failed to send SMS to {recipient}: {e}")

def send_whatsapp(body):
    if not all([TW_SID, TW_TOKEN, TW_FROM_WA]) or "XXX" in (TW_FROM_WA or ""):
        logging.warning("Twilio WhatsApp credentials not configured, skipping WhatsApp notification")
        return
    
    if not WA_RECIPIENTS:
        logging.warning("No WhatsApp recipients configured, skipping WhatsApp notification")
        return

    # Clean up phone numbers (strip whitespace)
    recipients = [phone.strip() for phone in WA_RECIPIENTS if phone.strip()]
    
    client = TwilioClient(TW_SID, TW_TOKEN)
    
    for recipient in recipients:
        try:
            client.messages.create(body=body, from_=f"whatsapp:{TW_FROM_WA}", to=f"whatsapp:{recipient}")
            logging.info(f"WhatsApp sent successfully to {recipient}")
        except Exception as e:
            logging.error(f"Failed to send WhatsApp to {recipient}: {e}")

# ——— Main loop ———
def main():
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start health check server in background (for fly.io)
    if os.getenv("ENABLE_HEALTH_SERVER", "true").lower() == "true":
        try:
            from health import start_health_server
            health_thread = threading.Thread(target=start_health_server, daemon=True)
            health_thread.start()
            logging.info("Health check server started")
        except ImportError:
            logging.warning("Health server not available")
    
    # load last count or initialize
    if LAST_COUNT_FILE.exists():
        last = int(LAST_COUNT_FILE.read_text().strip())
    else:
        last = fetch_habitacional_count()
        LAST_COUNT_FILE.write_text(str(last))
        logging.info(f"Initialized last_count = {last}")

    logging.info("Starting monitor loop...")
    while not shutdown_requested:
        try:
            current = fetch_habitacional_count()
            logging.info(f"Fetched habitacional={current} (last={last})")
            if current > last:
                diff = current - last
                msg = f"{diff} new habitacional listing(s) available! Now: {current}"
                logging.info(f"🎉 New listings detected! Sending notifications...")

                # notify (each function handles its own error checking)
                try:
                    send_push(msg)
                except Exception as e:
                    logging.error(f"Pushover notification failed: {e}")

                try:
                    send_email("New Habitacional Listing", msg)
                except Exception as e:
                    logging.error(f"Email notification failed: {e}")

                try:
                    send_sms(msg)
                except Exception as e:
                    logging.error(f"SMS notification failed: {e}")

                try:
                    send_whatsapp(msg)
                except Exception as e:
                    logging.error(f"WhatsApp notification failed: {e}")

                # update last
                last = current
                LAST_COUNT_FILE.write_text(str(last))
                logging.info(f"Updated last count to {last}")
            if not shutdown_requested:
                time.sleep(POLL_INTERVAL)
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            if not shutdown_requested:
                time.sleep(POLL_INTERVAL)
    
    logging.info("Monitor stopped gracefully.")
    sys.exit(0)

if __name__ == "__main__":
    main()
