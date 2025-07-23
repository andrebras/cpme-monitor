#!/usr/bin/env python3
"""Test run the monitor for a few iterations"""

import logging
import sys
import os
import time
from pathlib import Path

# Add parent directory to path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import fetch_habitacional_count
from src.notifications import send_push, send_email, send_sms, send_whatsapp

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

LAST_COUNT_FILE = Path("last_count.txt")
POLL_INTERVAL = 5  # seconds (shorter for testing)

def test_run(iterations=3):
    """Run the monitor logic for a few iterations"""
    
    # Load or initialize last count
    if LAST_COUNT_FILE.exists():
        last = int(LAST_COUNT_FILE.read_text().strip())
        logging.info(f"Loaded last_count = {last}")
    else:
        last = fetch_habitacional_count()
        LAST_COUNT_FILE.write_text(str(last))
        logging.info(f"Initialized last_count = {last}")

    logging.info(f"Starting {iterations} test iterations (polling every {POLL_INTERVAL}s)...")
    
    for i in range(iterations):
        try:
            current = fetch_habitacional_count()
            logging.info(f"[{i+1}/{iterations}] Fetched count={current} (last={last})")
            
            if current > last:
                diff = current - last
                msg = f"{diff} new listing(s) available! Now: {current}"
                logging.info(f"🎉 New listings detected! Would send notifications...")
                
                # Test notification functions (they'll skip if not configured)
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
                
                # Update last
                last = current
                LAST_COUNT_FILE.write_text(str(last))
                logging.info(f"Updated last count to {last}")
            
            if i < iterations - 1:  # Don't sleep after last iteration
                time.sleep(POLL_INTERVAL)
                
        except Exception as e:
            logging.error(f"Error in test loop: {e}")
            if i < iterations - 1:
                time.sleep(POLL_INTERVAL)
    
    logging.info("✅ Test run completed successfully!")

if __name__ == "__main__":
    test_run()