#!/usr/bin/env python3
"""Test script for notification systems"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.notifications import send_push, send_email, send_sms, send_whatsapp

load_dotenv()

def test_pushover():
    """Test Pushover notification"""
    try:
        if not os.getenv("PUSHOVER_USER_KEY") or not os.getenv("PUSHOVER_API_TOKEN"):
            print("❌ Pushover: Missing credentials")
            return False
        
        send_push("Test notification from CPME monitor")
        print("✅ Pushover: Test sent successfully")
        return True
    except Exception as e:
        print(f"❌ Pushover: {e}")
        return False

def test_email():
    """Test email notification"""
    try:
        if not os.getenv("GMAIL_EMAIL") or not os.getenv("GMAIL_PASSWORD"):
            print("❌ Email: Missing credentials")
            return False
        
        if not os.getenv("EMAIL_RECIPIENTS"):
            print("❌ Email: No recipients configured")
            return False
        
        recipients = os.getenv("EMAIL_RECIPIENTS").split(",")
        print(f"📧 Testing email to {len(recipients)} recipient(s): {', '.join(r.strip() for r in recipients)}")
        
        send_email("Test CPME Monitor", "This is a test email from your CPME monitor.")
        print("✅ Email: Test sent successfully")
        return True
    except Exception as e:
        print(f"❌ Email: {e}")
        return False

def test_sms():
    """Test SMS notification"""
    try:
        required_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_SMS"]
        if not all(os.getenv(var) and "XXX" not in os.getenv(var, "") for var in required_vars):
            print("❌ SMS: Missing or placeholder credentials")
            return False
        
        if not os.getenv("SMS_RECIPIENTS"):
            print("❌ SMS: No recipients configured")
            return False
        
        recipients = os.getenv("SMS_RECIPIENTS").split(",")
        print(f"📱 Testing SMS to {len(recipients)} recipient(s): {', '.join(r.strip() for r in recipients)}")
        
        send_sms("Test SMS from CPME monitor")
        print("✅ SMS: Test sent successfully")
        return True
    except Exception as e:
        print(f"❌ SMS: {e}")
        return False

def test_whatsapp():
    """Test WhatsApp notification"""
    try:
        required_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_WHATSAPP"]
        if not all(os.getenv(var) and "XXX" not in os.getenv(var, "") for var in required_vars):
            print("❌ WhatsApp: Missing or placeholder credentials")
            return False
        
        if not os.getenv("WHATSAPP_RECIPIENTS"):
            print("❌ WhatsApp: No recipients configured")
            return False
        
        recipients = os.getenv("WHATSAPP_RECIPIENTS").split(",")
        print(f"💬 Testing WhatsApp to {len(recipients)} recipient(s): {', '.join(r.strip() for r in recipients)}")
        
        send_whatsapp("Test WhatsApp from CPME monitor")
        print("✅ WhatsApp: Test sent successfully")
        return True
    except Exception as e:
        print(f"❌ WhatsApp: {e}")
        return False

if __name__ == "__main__":
    print("Testing notification systems...")
    print("=" * 40)
    
    results = [
        test_pushover(),
        test_email(), 
        test_sms(),
        test_whatsapp()
    ]
    
    print("=" * 40)
    successful = sum(results)
    print(f"Results: {successful}/4 notification systems working")
    
    if successful == 0:
        print("\n⚠️  No notification systems are configured. Please update your .env file with valid credentials.")
    elif successful < 4:
        print(f"\n⚠️  {4-successful} notification system(s) need configuration.")