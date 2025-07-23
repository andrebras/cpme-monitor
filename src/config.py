"""
Configuration management for CPME Monitor.

Centralizes all environment variable handling.
"""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# File paths
LAST_COUNT_FILE = Path(os.getenv("LAST_COUNT_FILE", "last_count.txt"))

# Monitor settings
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))
ENABLE_HEALTH_SERVER = os.getenv("ENABLE_HEALTH_SERVER", "true").lower() == "true"
HEALTH_PORT = int(os.getenv("HEALTH_PORT", "8080"))

# Pushover settings
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")

# Gmail settings
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "").split(",") if os.getenv("EMAIL_RECIPIENTS") else []

# Twilio settings
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_SMS = os.getenv("TWILIO_FROM_SMS")
SMS_RECIPIENTS = os.getenv("SMS_RECIPIENTS", "").split(",") if os.getenv("SMS_RECIPIENTS") else []
TWILIO_FROM_WHATSAPP = os.getenv("TWILIO_FROM_WHATSAPP")
WHATSAPP_RECIPIENTS = os.getenv("WHATSAPP_RECIPIENTS", "").split(",") if os.getenv("WHATSAPP_RECIPIENTS") else []

# Clean up recipient lists (remove empty strings)
EMAIL_RECIPIENTS: List[str] = [email.strip() for email in EMAIL_RECIPIENTS if email.strip()]
SMS_RECIPIENTS: List[str] = [phone.strip() for phone in SMS_RECIPIENTS if phone.strip()]
WHATSAPP_RECIPIENTS: List[str] = [phone.strip() for phone in WHATSAPP_RECIPIENTS if phone.strip()]