FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browser
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY .. .

# Create data directory for persistent state
RUN mkdir -p /app/data
ENV LAST_COUNT_FILE=/app/data/last_count.txt

# Expose health check port
EXPOSE 8080

# Run the monitor
CMD ["python", "main.py"]