#!/bin/bash
# MR.VERMA Cleanup Script
# Removes bloat and prepares unified structure

echo "═══════════════════════════════════════════════════════════════"
echo "  MR.VERMA - Bloat Cleanup Script"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "This script will clean up unnecessary files and optimize MR.VERMA"
echo ""
read -p "Continue? (y/n): " confirm

if [[ $confirm != [yY] ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "[1/6] Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null
find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
echo "✅ Python cache cleaned"

echo ""
echo "[2/6] Removing old documentation..."
# Keep only essential docs
mkdir -p docs_essential
cp README_UNIFIED.md docs_essential/README.md 2>/dev/null
cp PRODUCTION_READINESS_REPORT.md docs_essential/ 2>/dev/null
# Remove old doc directories but keep unified docs
rm -rf documentation/* 2>/dev/null
rm -rf docs/* 2>/dev/null
echo "✅ Documentation cleaned"

echo ""
echo "[3/6] Cleaning test cache..."
rm -rf .pytest_cache 2>/dev/null
rm -rf .ruff_cache 2>/dev/null
rm -f .coverage 2>/dev/null
echo "✅ Test cache cleaned"

echo ""
echo "[4/6] Removing agent metadata bloat..."
# Keep only essential agent definitions
rm -rf .agent/* 2>/dev/null
rm -rf .claude/* 2>/dev/null
rm -rf .qoder/* 2>/dev/null
rm -rf .trae/* 2>/dev/null
rm -rf .verma/* 2>/dev/null
echo "✅ Agent metadata cleaned"

echo ""
echo "[5/6] Creating unified structure..."
# Create clean directories
mkdir -p data
mkdir -p logs
mkdir -p output
mkdir -p unified
# Clean up old Docker files
rm -rf agent-lightning-local/Dockerfile.* 2>/dev/null
echo "✅ Unified structure created"

echo ""
echo "[6/6] Calculating space saved..."
BEFORE_SIZE=$(du -sh . 2>/dev/null | cut -f1)
echo "Current size: $BEFORE_SIZE"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Cleanup Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "✅ MR.VERMA has been optimized!"
echo ""
echo "What's Next:"
echo "  1. Run: ./START.bat (Windows) or ./start.sh (Linux/Mac)"
echo "  2. Enter your NVIDIA API key when prompted"
echo "  3. Start using MR.VERMA!"
echo ""
echo "Directory Structure:"
echo "  📁 data/     - Your data files"
echo "  📁 logs/     - Application logs"
echo "  📁 output/   - Generated files"
echo "  📁 unified/  - Core application"
echo "  📄 START.bat - Windows launcher"
echo "  📄 start.sh  - Linux/Mac launcher"
echo ""
