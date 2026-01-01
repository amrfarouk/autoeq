#!/bin/bash
# Deploy AutoEQ to ex63 production server
set -e

SERVER="ex63"
REMOTE_DIR="/root/autoeq"
GROQ_KEY_FILE="$HOME/.groq_api_key"

echo "=============================================="
echo "AutoEQ Deployment to ex63"
echo "=============================================="

# Check SSH connectivity
echo "[1/5] Checking SSH connectivity..."
if ! ssh -o ConnectTimeout=10 $SERVER "echo 'Connected'" 2>/dev/null; then
    echo "ERROR: Cannot connect to $SERVER"
    echo "Try: ssh $SERVER"
    exit 1
fi

# Sync files
echo "[2/5] Syncing files to $SERVER..."
rsync -avz --exclude='.git' --exclude='node_modules' --exclude='data/soundcloud_likes.json' --exclude='data/track_clusters.json' \
    . $SERVER:$REMOTE_DIR/

# Setup environment
echo "[3/5] Setting up environment..."
if [ -f "$GROQ_KEY_FILE" ]; then
    GROQ_KEY=$(cat "$GROQ_KEY_FILE" | grep -v "^#" | head -1)
    ssh $SERVER "echo 'GROQ_API_KEY=$GROQ_KEY' > $REMOTE_DIR/.env"
    echo "  GROQ_API_KEY configured"
else
    echo "  WARNING: No GROQ_API_KEY found at $GROQ_KEY_FILE"
fi

# Build and deploy
echo "[4/5] Building and starting container..."
ssh $SERVER "cd $REMOTE_DIR && docker-compose down 2>/dev/null || true && docker-compose build && docker-compose up -d"

# Verify deployment
echo "[5/5] Verifying deployment..."
sleep 5
if ssh $SERVER "curl -sf http://localhost:8890/health" | grep -q "healthy"; then
    echo ""
    echo "=============================================="
    echo "DEPLOYMENT SUCCESS"
    echo "=============================================="
    echo "Dashboard: http://88.198.232.12:8890"
    echo "Health:    http://88.198.232.12:8890/health"
    echo ""
else
    echo "WARNING: Health check failed. Check logs with:"
    echo "  ssh $SERVER 'docker logs autoeq'"
fi
