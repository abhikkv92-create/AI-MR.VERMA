#!/bin/bash
# ============================================================================
# MR.VERMA Unified Startup Script (Unix/Linux/Mac)
# Platform: OPENCODE, TRAE.AI, Local, Docker
# Version: 2.0.0
# ============================================================================

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "============================================================"
echo "  🕸️  MR.VERMA SPIDER WEB ORCHESTRATOR v2.0.0  🕸️"
echo "============================================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed or not in PATH${NC}"
    echo "Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}[✓]${NC} Node.js detected: $(node --version)"

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}[i]${NC} Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}[✓]${NC} Dependencies ready"

# Check for platform-specific flags
case "$1" in
    opencode)
        echo -e "${BLUE}[i]${NC} Starting in OPENCODE mode..."
        export OPENCODE_ENV=true
        ;;
    traeai)
        echo -e "${BLUE}[i]${NC} Starting in TRAE.AI mode..."
        export TRAE_AI_ENV=true
        ;;
    local)
        echo -e "${BLUE}[i]${NC} Starting in LOCAL mode..."
        ;;
    docker)
        echo -e "${BLUE}[i]${NC} Starting in DOCKER mode..."
        if [ -f "docker-compose.yml" ]; then
            docker-compose up -d
            echo ""
            echo -e "${GREEN}✅${NC} Docker containers started!"
            echo "Dashboard: http://localhost:8551"
            echo "Assistant: http://localhost:8550"
        else
            echo -e "${RED}❌ docker-compose.yml not found!${NC}"
            exit 1
        fi
        exit 0
        ;;
    *)
        # Auto-detect platform
        if [ -f ".opencode" ]; then
            echo -e "${BLUE}[i]${NC} Auto-detected OPENCODE platform"
            export OPENCODE_ENV=true
        elif [ -f ".trae" ]; then
            echo -e "${BLUE}[i]${NC} Auto-detected TRAE.AI platform"
            export TRAE_AI_ENV=true
        else
            echo -e "${BLUE}[i]${NC} Auto-detected LOCAL platform"
        fi
        ;;
esac

echo ""
echo "🚀 Initializing MR.VERMA SpiderWeb..."
echo "────────────────────────────────────────────────────────────"
echo ""

node core/startup.js "$@"

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}❌ Startup failed!${NC}"
    exit 1
fi
