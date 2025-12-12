FROM python:3.11-slim

# Install cron + tools you need for history (awscli, lz4)
RUN apt-get update && apt-get install -y \
    cron \
    lz4 \
    awscli \
    && rm -rf /var/lib/apt/lists/*

# Python logs straight to stdout and can import from /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Workdir inside container
WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Ensure log file exists
RUN mkdir -p /var/log && touch /var/log/hourly_funding.log

# Install crontab
COPY crontab.txt /etc/cron.d/funding-cron
RUN chmod 0644 /etc/cron.d/funding-cron && crontab /etc/cron.d/funding-cron

# Run cron in foreground when container starts
CMD ["cron", "-f"]
