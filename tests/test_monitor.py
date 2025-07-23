#!/usr/bin/env python3
"""Test the main monitoring functionality"""

import logging
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import fetch_habitacional_count

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def test_monitor_logic():
    """Test the core monitoring logic"""
    
    # Test file for tracking count
    test_file = Path("test_last_count.txt")
    
    try:
        # Get current count
        current = fetch_habitacional_count()
        print(f"Current listing count: {current}")
        
        # Simulate first run (no previous count)
        if test_file.exists():
            test_file.unlink()
        
        # Test initialization logic
        if not test_file.exists():
            test_file.write_text(str(current))
            print(f"✅ Initialized test count file with: {current}")
        
        # Test reading existing count
        last = int(test_file.read_text().strip())
        print(f"Read last count from file: {last}")
        
        # Simulate checking for changes
        if current > last:
            diff = current - last
            print(f"🎉 Would send notification: {diff} new listing(s)!")
        elif current < last:
            print(f"📉 Count decreased by {last - current}")
        else:
            print("📊 No change in listing count")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in monitor logic: {e}")
        return False
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    print("Testing monitor logic...")
    print("=" * 40)
    
    success = test_monitor_logic()
    
    print("=" * 40)
    if success:
        print("✅ Monitor logic test passed!")
        print("\nTo run the full monitor:")
        print("  python main.py")
        print("\nNote: Configure your .env file for notifications to work.")
    else:
        print("❌ Monitor logic test failed!")