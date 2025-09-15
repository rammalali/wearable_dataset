FROM python:3.12-slim

# System deps required by Chrome + basics
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates xdg-utils \
    # Chrome runtime libraries (common culprits)
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 \
    libdbus-1-3 libdrm2 libexpat1 libgbm1 libglib2.0-0 \
    libgtk-3-0 libnspr4 libnss3 libu2f-udev libx11-6 \
    libx11-xcb1 libxcb1 libxcomposite1 libxdamage1 libxext6 \
    libxi6 libxrandr2 libxrender1 libxshmfence1 libxtst6 \
    fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
 && apt-get update \
 && apt-get install -y /tmp/chrome.deb \
 && rm -f /tmp/chrome.deb

# Python deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Point Plotly/Kaleido to Chrome and add safe flags for containers
ENV PLOTLY_CHROME="/usr/bin/google-chrome" \
    PLOTLY_CHROME_ARGS="--headless --no-sandbox --disable-dev-shm-usage"

# Your app
COPY . .
EXPOSE 5000

# Gunicorn tuning — adjust workers/threads as needed
# Assumes your Flask app is created as `app` inside app.py (i.e., `app = Flask(__name__)`)
ENV WEB_WORKERS=5 \
    WEB_THREADS=2 \
    GUNICORN_TIMEOUT=60

# Run via Gunicorn
CMD ["bash", "-lc", "gunicorn app:app \
  --bind 0.0.0.0:5000 \
  --workers ${WEB_WORKERS} \
  --threads ${WEB_THREADS} \
  --timeout ${GUNICORN_TIMEOUT} \
  --preload \
  --max-requests 100 \
  --max-requests-jitter 200"]