#!/bin/bash
# Docker Validation Script for MR.VERMA
# This script validates the Docker setup and identifies any issues

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  MR.VERMA Docker Validation Script"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        ERRORS=$((ERRORS + 1))
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

echo "[1/10] Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    print_status 0 "Docker installed: $DOCKER_VERSION"
else
    print_status 1 "Docker not installed"
fi

echo ""
echo "[2/10] Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    print_status 0 "Docker Compose installed: $COMPOSE_VERSION"
else
    print_status 1 "Docker Compose not installed"
fi

echo ""
echo "[3/10] Checking required files..."
FILES=(
    "docker-compose.yml"
    "Dockerfile.collector"
    "Dockerfile.trainer"
    ".env"
    "scripts/docker-entrypoint.sh"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        print_status 0 "Found: $file"
    else
        print_status 1 "Missing: $file"
    fi
done

echo ""
echo "[4/10] Checking .env configuration..."
if [ -f ".env" ]; then
    if grep -q "NVIDIA_API_KEY" .env; then
        API_KEY=$(grep "NVIDIA_API_KEY" .env | cut -d'=' -f2)
        if [ -n "$API_KEY" ] && [ "$API_KEY" != "your_api_key_here" ]; then
            print_status 0 "NVIDIA_API_KEY configured"
        else
            print_warning "NVIDIA_API_KEY is empty or set to placeholder"
        fi
    else
        print_status 1 "NVIDIA_API_KEY not found in .env"
    fi
else
    print_status 1 ".env file not found"
fi

echo ""
echo "[5/10] Validating docker-compose.yml syntax..."
if docker-compose config > /dev/null 2>&1; then
    print_status 0 "docker-compose.yml syntax is valid"
else
    print_status 1 "docker-compose.yml has syntax errors"
fi

echo ""
echo "[6/10] Checking Dockerfiles..."
for df in Dockerfile.collector Dockerfile.trainer; do
    if [ -f "$df" ]; then
        if grep -q "FROM" "$df"; then
            print_status 0 "$df has valid FROM instruction"
        else
            print_status 1 "$df missing FROM instruction"
        fi
    fi
done

echo ""
echo "[7/10] Checking Python dependencies..."
if [ -f "agent-lightning-local/requirements.collector.txt" ]; then
    if grep -q "flask" agent-lightning-local/requirements.collector.txt; then
        print_status 0 "Flask dependency found"
    else
        print_warning "Flask dependency missing"
    fi
    
    if grep -q "gunicorn" agent-lightning-local/requirements.collector.txt; then
        print_status 0 "Gunicorn dependency found"
    else
        print_warning "Gunicorn dependency missing"
    fi
fi

echo ""
echo "[8/10] Checking network configuration..."
if grep -q "networks:" docker-compose.yml; then
    print_status 0 "Docker networks configured"
else
    print_status 1 "Docker networks not configured"
fi

if grep -q "volumes:" docker-compose.yml; then
    print_status 0 "Docker volumes configured"
else
    print_status 1 "Docker volumes not configured"
fi

echo ""
echo "[9/10] Testing Docker build (this may take a few minutes)..."
if docker build -f Dockerfile.collector -t mrverma-collector-test . > /tmp/docker-build.log 2>&1; then
    print_status 0 "Dockerfile.collector builds successfully"
    docker rmi mrverma-collector-test > /dev/null 2>&1
else
    print_status 1 "Dockerfile.collector build failed (check /tmp/docker-build.log)"
fi

echo ""
echo "[10/10] Pre-flight checks..."

# Check if ports are available
if ! netstat -tuln 2>/dev/null | grep -q ":8550 "; then
    print_status 0 "Port 8550 is available"
else
    print_warning "Port 8550 is already in use"
fi

if ! netstat -tuln 2>/dev/null | grep -q ":19530 "; then
    print_status 0 "Port 19530 is available"
else
    print_warning "Port 19530 is already in use"
fi

# Check disk space
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    print_status 0 "Disk space is sufficient (${DISK_USAGE}% used)"
else
    print_warning "Disk space is running low (${DISK_USAGE}% used)"
fi

# Check memory
if command -v free &> /dev/null; then
    MEM_AVAILABLE=$(free -m | awk 'NR==2{print $7}')
    if [ "$MEM_AVAILABLE" -gt 2048 ]; then
        print_status 0 "Memory is sufficient (${MEM_AVAILABLE}MB available)"
    else
        print_warning "Memory might be insufficient (${MEM_AVAILABLE}MB available, recommend 2GB+)"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Validation Summary"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "You can now start MR.VERMA with:"
    echo "  docker-compose up -d"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    echo ""
    echo "System should work but review warnings above."
    echo "Start with: docker-compose up -d"
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) and $WARNINGS warning(s) found${NC}"
    echo ""
    echo "Please fix the errors above before starting MR.VERMA."
    exit 1
fi
