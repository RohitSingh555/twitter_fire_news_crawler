# Use official Python image
FROM python:3.11-slim

# Install system dependencies for Chrome and ChromeDriver
RUN apt-get update && \
    apt-get install -y wget gnupg2 unzip && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Set display port to avoid crash
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set environment variable for OpenAI API key (can be overridden at runtime)
ENV OPENAI_API_KEY=""

# Optional: copy .env if you want to use it (uncomment if needed)
# COPY .env .

# Set Chrome options for headless operation
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_OPTIONS="--headless --no-sandbox --disable-dev-shm-usage --disable-gpu --window-size=1920,1080"

# Default command: run the main script
CMD ["python", "tweet_fire_search.py"] 