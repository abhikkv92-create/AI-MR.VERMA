@echo off
chcp 65001 >nul
title MR.VERMA Enhanced - AI Intelligence Platform
cls

echo.
echo    ███╗   ███╗██████╗      ██╗   ██╗███████╗██████╗ ███╗   ███╗ █████╗
echo    ████╗ ████║██╔══██╗     ██║   ██║██╔════╝██╔══██╗████╗ ████║██╔══██╗
echo    ██╔████╔██║██████╔╝     ██║   ██║█████╗  ██████╔╝██╔████╔██║███████║
echo    ██║╚██╔╝██║██╔══██╗     ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══██║
echo    ██║ ╚═╝ ██║██║  ██║      ╚████╔╝ ███████╗██║  ██║██║ ╚═╝ ██║██║  ██║
echo    ╚═╝     ╚═╝╚═╝  ╚═╝       ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝
echo.
echo           🤖 ENHANCED AI PLATFORM with AGENTS, SKILLS & WORKFLOWS
echo.

:: Set working directory
cd /d "%~dp0"

:: Check prerequisites
echo    [1/5] 🔍 Checking system requirements...
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    ❌ Python not found.
    echo    Please install Python 3.9+ from https://python.org
    echo.
    start https://python.org/downloads
    pause
    exit /b 1
)
echo    ✅ Python is installed

:: Check Docker (optional)
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    ⚠️  Docker not found. Using local mode.
    set DOCKER_AVAILABLE=0
) else (
    echo    ✅ Docker is installed
    set DOCKER_AVAILABLE=1
)

:: Check NVIDIA API Key
if not exist .env (
    echo.
    echo    [2/5] 🔑 First-time setup detected...
    echo.
    echo    To use MR.VERMA, you need a free NVIDIA API key.
    echo    Get one at: https://build.nvidia.com/explore/discover
    echo.
    set /p NVIDIA_KEY="    Paste your NVIDIA API key here: "
    echo NVIDIA_API_KEY=%NVIDIA_KEY% > .env
    echo NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions >> .env
    echo NVIDIA_MODEL=moonshotai/kimi-k2.5 >> .env
    echo LOG_LEVEL=INFO >> .env
    echo    ✅ Configuration saved to .env
) else (
    echo    ✅ Configuration found
)

echo.
echo    [3/5] 📦 Installing dependencies (one-time setup)...
echo.

:: Install Python dependencies
if not exist venv (
    python -m venv venv
    echo    ✅ Virtual environment created
)

call venv\Scripts\activate.bat

:: Install requirements
if exist requirements.unified.txt (
    pip install -q -r requirements.unified.txt
) else (
    pip install -q flask flask-cors gunicorn requests openai numpy pandas psutil python-dotenv rich prompt-toolkit pydantic pyyaml cryptography
)

if %errorlevel% neq 0 (
    echo    ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo    ✅ Dependencies installed

echo.
echo    [4/5] 🚀 Starting MR.VERMA services...
echo.

:: Start Docker services if available
if %DOCKER_AVAILABLE%==1 (
    echo    Starting AI Brain (Docker)...    
    docker-compose up -d --quiet-pull 2>nul
    if %errorlevel% equ 0 (
        echo    ✅ AI Brain is running
        timeout /t 3 /nobreak >nul
    ) else (
        echo    ⚠️  Docker services not started (using local mode)
    )
)

:: Create necessary directories
if not exist data mkdir data
if not exist logs mkdir logs
if not exist output mkdir output

echo.
echo    [5/5] 🎯 Launching MR.VERMA Enhanced Interface...
echo.
echo    ════════════════════════════════════════════════════════════
echo    🎉 MR.VERMA Enhanced is ready! Press any key to start...
echo    ════════════════════════════════════════════════════════════
echo.
pause >nul

:: Launch the enhanced interface
python unified\mrverma_enhanced.py

:: Cleanup on exit
call venv\Scripts\deactivate.bat 2>nul
exit /b 0
