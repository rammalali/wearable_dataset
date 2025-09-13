# Use official Python image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt first for dependency install
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose Flask default port
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Run the Flask app
CMD ["python", "app.py"]
