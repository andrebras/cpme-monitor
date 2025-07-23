"""
CPME Monitor - Main Application.

Monitors CPME website for new listings and sends notifications.
"""

import logging
import os
import signal
import sys
import threading
import time
from typing import Any, NoReturn

from .config import LAST_COUNT_FILE, POLL_INTERVAL, ENABLE_HEALTH_SERVER
from .scraper import fetch_habitacional_count
from .notifications import send_all_notifications

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum: int, frame: Any) -> None:
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    logging.info("Shutdown signal received. Finishing current check...")
    shutdown_requested = True

def main() -> NoReturn:
    """Main monitoring loop."""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start health check server in background (for fly.io)
    if ENABLE_HEALTH_SERVER:
        try:
            from .health import start_health_server
            health_thread = threading.Thread(target=start_health_server, daemon=True)
            health_thread.start()
            logging.info("Health check server thread started")
            # Give it a moment to start and log any immediate errors
            time.sleep(1)
        except ImportError:
            logging.warning("Health server not available")
        except Exception as e:
            logging.error(f"Failed to start health server: {e}")
    
    # Load or initialize last count  
    if LAST_COUNT_FILE.exists():
        last = int(LAST_COUNT_FILE.read_text().strip())
        logging.info(f"Loaded last_count = {last}")
    else:
        # First run - use initial count (default 0, configurable)
        initial_count = int(os.getenv("INITIAL_COUNT", "0"))
        last = initial_count
        LAST_COUNT_FILE.write_text(str(last))
        logging.info(f"First run - initialized last_count = {last}")

    logging.info(f"Starting monitor loop (checking every {POLL_INTERVAL}s)...")
    
    while not shutdown_requested:
        try:
            current = fetch_habitacional_count()
            logging.info(f"Fetched count={current} (last={last})")
            
            if current != last:
                if current > last:
                    diff = current - last
                    message = f"Listings updated! Count: {current} (+{diff}). New opportunities may be available. Check https://cpme.fyidigital.pt/arrendamento"
                else:
                    diff = last - current
                    message = f"Listings updated! Count: {current} (-{diff}). New opportunities may be available (listings can be edited/replaced). Check https://cpme.fyidigital.pt/arrendamento"
                
                # Send all notifications for any change
                send_all_notifications(message)
                
                # Update last count
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