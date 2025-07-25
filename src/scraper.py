"""
Web scraping functionality for CPME website.
"""

import logging
from playwright.sync_api import sync_playwright
from .config import CPME_URL


def fetch_habitacional_count() -> int:
    """
    Scrape the CPME website to get current listing count.
    
    Returns:
        int: Number of available listings, 0 if none found or error.
    """
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(CPME_URL)
            page.wait_for_load_state("networkidle")
            
            # Find all "Andares disponíveis: X" elements
            counts = page.evaluate("""
                Array.from(document.querySelectorAll('*'))
                    .map(el => el.textContent.trim())
                    .filter(text => text.startsWith('Andares disponíveis'))
                    .map(text => parseInt(text.match(/\\d+/)[0]));
            """)
            
            browser.close()
            return counts[0] if counts else 0
            
    except Exception as e:
        logging.error("Error scraping website: %s", e)
        return 0