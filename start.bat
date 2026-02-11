@echo off
REM ============================================================================
REM MR.VERMA Unified Startup Script
REM Platform: OPENCODE, TRAE.AI, Local, Docker
REM Version: 2.0.0
REM ============================================================================

title MR.VERMA SpiderWeb Initialization
color 0A

echo.
echo  ============================================================
echo   🕸️  MR.VERMA SPIDER WEB ORCHESTRATOR v2.0.0  🕸️
echo  ============================================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ Node.js is not installed or not in PATH
    echo  Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)

echo  [✓] Node.js detected

REM Check if dependencies are installed
if not exist "node_modules" (
    echo  [i] Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo  ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo  [✓] Dependencies ready

REM Check for platform-specific flags
if "%~1"=="opencode" (
    echo  [i] Starting in OPENCODE mode...
    set OPENCODE_ENV=true
    goto start_node
)

if "%~1"=="traeai" (
    echo  [i] Starting in TRAE.AI mode...
    set TRAE_AI_ENV=true
    goto start_node
)

if "%~1"=="local" (
    echo  [i] Starting in LOCAL mode...
    goto start_node
)

if "%~1"=="docker" (
    echo  [i] Starting in DOCKER mode...
    goto start_docker
)

REM Auto-detect platform
if exist ".opencode" (
    echo  [i] Auto-detected OPENCODE platform
    set OPENCODE_ENV=true
) else if exist ".trae" (
    echo  [i] Auto-detected TRAE.AI platform
    set TRAE_AI_ENV=true
) else (
    echo  [i] Auto-detected LOCAL platform
)

:start_node
echo.
echo  🚀 Initializing MR.VERMA SpiderWeb...
echo  ────────────────────────────────────────────────────────────
echo.

node core/startup.js %*

if errorlevel 1 (
    echo.
    echo  ❌ Startup failed!
    pause
    exit /b 1
)

pause
exit /b 0

:start_docker
echo.
echo  🐳 Starting Docker containers...
echo  ────────────────────────────────────────────────────────────
echo.

cd /d "%~dp0"

if not exist "docker-compose.yml" (
    echo  ❌ docker-compose.yml not found!
    pause
    exit /b 1
)

docker-compose up -d

if errorlevel 1 (
    echo  ❌ Docker failed to start!
    pause
    exit /b 1
)

echo.
echo  ✅ Docker containers started!
echo  Dashboard: http://localhost:8551
echo  Assistant: http://localhost:8550
echo.

pause
exit /b 0
