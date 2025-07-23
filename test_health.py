#!/usr/bin/env python3
"""Test script for the health check server"""

import requests
import threading
import time
import logging
from health import start_health_server

def test_health_server():
    """Test the health check endpoint"""
    logging.basicConfig(level=logging.INFO)
    
    # Start health server in background
    print("Starting health server...")
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Give it a moment to start
    time.sleep(2)
    
    # Test health endpoint
    try:
        print("Testing health endpoint...")
        response = requests.get('http://localhost:8080/health', timeout=5)
        print(f'✅ Health check status: {response.status_code}')
        print(f'Response: {response.text}')
        
        if response.status_code in [200, 503]:  # Both are valid responses
            print("✅ Health server working correctly")
            return True
        else:
            print("❌ Unexpected status code")
            return False
            
    except Exception as e:
        print(f'❌ Health check failed: {e}')
        return False

if __name__ == "__main__":
    success = test_health_server()
    if success:
        print("\n🎉 Health server test passed!")
    else:
        print("\n💥 Health server test failed!")
        exit(1)