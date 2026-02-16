#!/bin/bash
# Docker Entrypoint Script for MR.VERMA Collector
# This script prepares the environment and starts the collector

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  MR.VERMA Intelligence Core - Container Startup"
echo "═══════════════════════════════════════════════════════════════"

# Create necessary directories
echo "[SETUP] Creating required directories..."
mkdir -p /app/data/interactions
mkdir -p /app/logs
mkdir -p /app/checkpoints
mkdir -p /app/config

# Set proper permissions
echo "[SETUP] Setting permissions..."
chmod -R 755 /app/data /app/logs /app/checkpoints

# Wait for dependencies
echo "[SETUP] Waiting for dependencies..."

# Wait for Milvus
if [ -n "$MILVUS_HOST" ]; then
    echo "[SETUP] Waiting for Milvus at $MILVUS_HOST:$MILVUS_PORT..."
    until curl -sf "http://$MILVUS_HOST:9091/healthz" > /dev/null 2>&1; do
        echo "[SETUP] Waiting for Milvus..."
        sleep 5
    done
    echo "[SETUP] Milvus is ready!"
fi

# Check NVIDIA API Key
echo "[SETUP] Checking NVIDIA API configuration..."
if [ -z "$NVIDIA_API_KEY" ]; then
    echo "[WARNING] NVIDIA_API_KEY not set! AI features will not work."
else
    echo "[SETUP] NVIDIA API Key configured."
fi

# Verify Python imports
echo "[SETUP] Verifying Python environment..."
python -c "import sys; print(f'Python version: {sys.version}')"
python -c "import flask; print(f'Flask version: {flask.__version__}')"
python -c "import requests; print(f'Requests version: {requests.__version__}')"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Starting MR.VERMA Collector..."
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Execute the main command
exec "$@"
