# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python monitoring script that tracks available apartment listings on the CPME website (https://cpme.fyidigital.pt/arrendamento) and sends notifications when new listings become available.

## Development Setup

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Install dependencies (if needed):
   ```bash
   pip install playwright requests python-dotenv twilio
   playwright install chromium
   ```

3. Create a `.env` file with required environment variables:
   - `PUSHOVER_USER_KEY` and `PUSHOVER_API_TOKEN` for push notifications
   - `GMAIL_EMAIL` and `GMAIL_PASSWORD` for email notifications
   - `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_SMS`, `TWILIO_TO_SMS` for SMS
   - `TWILIO_FROM_WHATSAPP`, `TWILIO_TO_WHATSAPP` for WhatsApp notifications

## Running the Application

```bash
python monitor.py
```

The script runs continuously, polling every 30 seconds and maintaining state in `last_count.txt`.

## Architecture

- **Single-file application**: All functionality is contained in `monitor.py`
- **Web scraping**: Uses Playwright to scrape apartment count from the CPME website
- **Multi-channel notifications**: Supports Pushover, email, SMS, and WhatsApp notifications
- **State persistence**: Tracks last known count in `last_count.txt` to detect changes
- **Error handling**: Continues running even if individual polling attempts fail

## Key Functions

- `fetch_habitacional_count()`: Scrapes the website using Playwright to get current apartment count
- `send_push()`, `send_email()`, `send_sms()`, `send_whatsapp()`: Notification functions for different channels
- `main()`: Main monitoring loop that polls and compares counts

## Dependencies

The project uses a virtual environment with these key packages:
- `playwright` for web browser automation
- `requests` for HTTP requests (Pushover API)
- `python-dotenv` for environment variable management
- `twilio` for SMS/WhatsApp notifications