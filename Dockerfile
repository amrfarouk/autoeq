# AutoEQ - Dynamic SoundCloud EQ Dashboard
# Daily auto-updating with AI-powered clustering via Groq

FROM python:3.12-slim

LABEL maintainer="VitaNova <admin@vitainfra.com>"
LABEL description="AutoEQ: SoundCloud Likes Analyzer with AI Clustering"
LABEL version="1.0.0"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY *.html ./
COPY *.css ./
COPY *.js ./

# Create directories
RUN mkdir -p /app/logs /app/data

# Setup nginx for serving static files
COPY nginx.conf /etc/nginx/sites-available/default

# Setup cron job for daily updates (3 AM UTC)
RUN echo "0 3 * * * cd /app && /usr/local/bin/python3 /app/src/daily_update.py >> /app/logs/cron.log 2>&1" > /etc/cron.d/autoeq-cron \
    && chmod 0644 /etc/cron.d/autoeq-cron \
    && crontab /etc/cron.d/autoeq-cron

# Startup script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start services
ENTRYPOINT ["/entrypoint.sh"]
