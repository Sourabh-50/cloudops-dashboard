# Use a lightweight official Python runtime
FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=Production
ENV APP_VERSION=1.0.0
ENV BUILD_NUMBER=001
ENV CLOUD_PROVIDER="AWS EC2"

# Set working directory
WORKDIR /app

# Install dependencies first for caching layers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the Flask development/Gunicorn port
EXPOSE 5000

# Create a non-privileged user and switch to it for production security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

# Run Gunicorn to serve the Flask app in production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
