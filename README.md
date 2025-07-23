# CPME Apartment Monitor

A simple monitor that tracks apartment listings on the CPME website and sends notifications when new listings appear.

## Features

- **Web scraping** of CPME apartment listings
- **Multi-channel notifications**: Pushover (iPhone), Email, SMS, WhatsApp
- **Multiple recipients** per notification type
- **Persistent state** to track changes
- **Graceful shutdown** handling
- **Health check endpoint** for monitoring

## Project Structure

```
cpme-monitor/
├── src/                    # Main application code
│   ├── monitor.py         # Main monitoring logic
│   ├── scraper.py         # Web scraping functionality
│   ├── notifications.py   # All notification systems
│   ├── health.py          # Health check server
│   └── config.py          # Configuration management
├── tests/                 # Test scripts
│   ├── test_notifications.py
│   ├── test_monitor.py
│   ├── test_health.py
│   └── test_run.py
├── deploy/                # Deployment configuration
│   ├── Dockerfile
│   ├── fly.toml
│   └── .dockerignore
├── main.py               # Entry point
└── requirements.txt      # Dependencies
```

## Local Development

1. **Clone and setup:**
   ```bash
   git clone <repository>
   cd cpme-notifier
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run locally:**
   ```bash
   python main.py
   ```

## Deploy to Fly.io

1. **Install fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and create app:**
   ```bash
   fly auth login
   fly launch --no-deploy
   ```

3. **Set secrets:**
   ```bash
   fly secrets set \
     PUSHOVER_USER_KEY="your_key" \
     PUSHOVER_API_TOKEN="your_token" \
     GMAIL_EMAIL="your_email@gmail.com" \
     GMAIL_PASSWORD="your_app_password" \
     EMAIL_RECIPIENTS="email1@domain.com,email2@domain.com"
   ```

4. **Deploy:**
   ```bash
   fly deploy
   ```

5. **Check status:**
   ```bash
   fly status
   fly logs
   ```

## Configuration

Environment variables:

- `POLL_INTERVAL` - Seconds between checks (default: 30)
- `ENABLE_HEALTH_SERVER` - Enable health endpoint (default: true)
- `HEALTH_PORT` - Health server port (default: 8080)

## Notifications

- **Pushover**: iPhone push notifications
- **Email**: Gmail SMTP with App Password
- **SMS**: Twilio SMS service
- **WhatsApp**: Twilio WhatsApp Business API

## Health Check

The service exposes a health endpoint at `/health` that returns:
- `200` - Service healthy
- `503` - Service unhealthy or not responding

## Cost Estimation

**Fly.io costs (approximate):**
- Basic app: ~$5-10/month
- Storage volume: ~$0.15/month

**Third-party services:**
- Pushover: Free (7.5k messages), then $5 one-time
- Gmail: Free
- Twilio SMS: ~$0.01 per message
- Twilio WhatsApp: ~$0.005 per message