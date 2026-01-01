#!/bin/bash
set -e

echo "=============================================="
echo "AutoEQ Container Starting"
echo "=============================================="

# Check for GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ]; then
    echo "WARNING: GROQ_API_KEY not set. AI clustering will fail."
fi

# Run initial update if data is empty
if [ ! -f /app/data/soundcloud_likes.json ] || [ ! -s /app/data/soundcloud_likes.json ]; then
    echo "No data found. Running initial fetch..."
    python3 /app/src/daily_update.py || echo "Initial update failed, will retry on schedule"
fi

# Start cron daemon
echo "Starting cron daemon..."
cron

# Start nginx in foreground
echo "Starting nginx..."
nginx -g 'daemon off;'
