FROM python:3.12-slim

# 1) System deps (wget, certs, fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

# 2) Install Chrome
RUN wget -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
 && apt-get update \
 && apt-get install -y /tmp/chrome.deb \
 && rm -f /tmp/chrome.deb

# 3) Python deps (make sure requirements includes plotly + kaleido, or pip them here)
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Point Plotly/Kaleido to Chrome with safe headless flags
ENV PLOTLY_CHROME="/usr/bin/google-chrome" \
    PLOTLY_CHROME_ARGS="--headless --no-sandbox --disable-dev-shm-usage"

# App files
COPY . .
EXPOSE 5000
ENV FLASK_APP=app.py FLASK_RUN_HOST=0.0.0.0 FLASK_RUN_PORT=5000
CMD ["python", "app.py"]
