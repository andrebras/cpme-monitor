#!/usr/bin/env python3
"""
Simple health check server for fly.io
Runs alongside the monitor to provide health status
"""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

from .config import HEALTH_PORT, LAST_COUNT_FILE

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_health_response()
        else:
            self.send_response(404)
            self.end_headers()

    def send_health_response(self):
        try:
            # Check if monitor is running (last_count.txt updated recently)
            if LAST_COUNT_FILE.exists():
                last_modified = datetime.fromtimestamp(LAST_COUNT_FILE.stat().st_mtime)
                age = datetime.now() - last_modified
                
                if age < timedelta(minutes=5):  # Consider healthy if updated in last 5 min
                    status = "healthy"
                    code = 200
                    last_count = LAST_COUNT_FILE.read_text().strip()
                    message = f"Monitor running. Last count: {last_count}, updated {age.seconds}s ago"
                else:
                    status = "unhealthy"
                    code = 503
                    message = f"Monitor not updated for {age.seconds}s"
            else:
                status = "starting"
                code = 200
                message = "Monitor starting up"
            
            response = {
                "status": status,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(error_response).encode())

    def log_message(self, format, *args):
        # Suppress HTTP logs to keep output clean
        pass

def start_health_server():
    """Start health check server in background thread"""
    server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
    logging.info(f"Health server starting on port {HEALTH_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    # Can be run standalone for testing
    logging.basicConfig(level=logging.INFO)
    start_health_server()