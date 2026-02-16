#!/bin/bash
# MR.VERMA Unified Start Script for Linux/Mac
# One-click launcher with automatic setup

clear

echo ""
echo "    ███╗   ███╗██████╗      ██╗   ██╗███████╗██████╗ ███╗   ███╗ █████╗"
echo "    ████╗ ████║██╔══██╗     ██║   ██║██╔════╝██╔══██╗████╗ ████║██╔══██╗"
echo "    ██╔████╔██║██████╔╝     ██║   ██║█████╗  ██████╔╝██╔████╔██║███████║"
echo "    ██║╚██╔╝██║██╔══██╗     ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══██║"
echo "    ██║ ╚═╝ ██║██║  ██║      ╚████╔╝ ███████╗██║  ██║██║ ╚═╝ ██║██║  ██║"
echo "    ╚═╝     ╚═╝╚═╝  ╚═╝       ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝"
echo ""
echo "                    🤖 Unified AI Intelligence Platform"
echo ""

# Set working directory
cd "$(dirname "$0")"

# Check prerequisites
echo "    [1/5] 🔍 Checking system requirements..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "    ❌ Python 3 not found."
    echo "    Please install Python 3.9+ from https://python.org"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi
echo "    ✅ Python is installed"

# Check Docker (optional)
if command -v docker &> /dev/null; then
    echo "    ✅ Docker is installed"
    DOCKER_AVAILABLE=1
else
    echo "    ⚠️  Docker not found. Using local mode."
    DOCKER_AVAILABLE=0
fi

# Check NVIDIA API Key
if [ ! -f .env ]; then
    echo ""
    echo "    [2/5] 🔑 First-time setup detected..."
    echo ""
    echo "    To use MR.VERMA, you need a free NVIDIA API key."
    echo "    Get one at: https://build.nvidia.com/explore/discover"
    echo ""
    read -p "    Paste your NVIDIA API key here: " NVIDIA_KEY
    echo "NVIDIA_API_KEY=$NVIDIA_KEY" > .env
    echo "NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions" >> .env
    echo "NVIDIA_MODEL=moonshotai/kimi-k2.5" >> .env
    echo "LOG_LEVEL=INFO" >> .env
    echo "    ✅ Configuration saved to .env"
else
    echo "    ✅ Configuration found"
fi

echo ""
echo "    [3/5] 📦 Installing dependencies (one-time setup)..."
echo ""

# Install Python dependencies
if [ ! -d venv ]; then
    python3 -m venv venv
    echo "    ✅ Virtual environment created"
fi

source venv/bin/activate
pip install -q -r requirements.unified.txt
if [ $? -ne 0 ]; then
    echo "    ❌ Failed to install dependencies"
    read -p "Press Enter to exit..."
    exit 1
fi
echo "    ✅ Dependencies installed"

echo ""
echo "    [4/5] 🚀 Starting MR.VERMA services..."
echo ""

# Start Docker services if available
if [ $DOCKER_AVAILABLE -eq 1 ]; then
    echo "    Starting AI Brain (Docker)..."    
    docker-compose up -d --quiet-pull 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "    ✅ AI Brain is running"
        sleep 3
    else
        echo "    ⚠️  Docker services not started (using local mode)"
    fi
fi

# Create necessary directories
mkdir -p data logs output

echo ""
echo "    [5/5] 🎯 Launching MR.VERMA Interface..."
echo ""
echo "    ════════════════════════════════════════════════════════════"
echo "    🎉 MR.VERMA is ready! Press any key to start..."
echo "    ════════════════════════════════════════════════════════════"
echo ""
read -n 1 -s

# Launch the unified interface
python3 unified/mrverma.py

# Cleanup on exit
deactivate 2>/dev/null
exit 0
