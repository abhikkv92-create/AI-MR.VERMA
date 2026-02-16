@echo off
chcp 65001 >nul
title MR.VERMA AUTONOMOUS - Self-Running AI Platform
cls

echo.
echo    ███╗   ███╗██████╗      ██╗   ██╗███████╗██████╗ ███╗   ███╗ █████╗
echo    ████╗ ████║██╔══██╗     ██║   ██║██╔════╝██╔══██╗████╗ ████║██╔══██╗
echo    ██╔████╔██║██████╔╝     ██║   ██║█████╗  ██████╔╝██╔████╔██║███████║
echo    ██║╚██╔╝██║██╔══██╗     ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══██║
echo    ██║ ╚═╝ ██║██║  ██║      ╚████╔╝ ███████╗██║  ██║██║ ╚═╝ ██║██║  ██║
echo    ╚═╝     ╚═╝╚═╝  ╚═╝       ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝
echo.
echo           🤖 AUTONOMOUS AI PLATFORM - NO API KEYS NEEDED 🤖
echo.
echo       ✓ Self-Running ✓ Auto-Detection ✓ VibeCoding ✓ Docker Integration
echo.

:: Set working directory
cd /d "%~dp0"

echo    [1/3] 🔍 Initializing Autonomous System...
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    ❌ Python not found. Please install Python 3.9+
    pause
    exit /b 1
)
echo    ✅ Python detected

:: Check Docker (optional but recommended)
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Docker detected - Infrastructure will be managed automatically
    set DOCKER_AVAILABLE=1
) else (
    echo    ⚠️  Docker not detected - Running in lightweight mode
    set DOCKER_AVAILABLE=0
)

echo.
echo    [2/3] 📦 Checking Dependencies...
echo.

:: Setup virtual environment
if not exist venv (
    python -m venv venv
    echo    ✅ Virtual environment created
)

call venv\Scripts\activate.bat

:: Install minimal dependencies (no API libraries needed!)
pip install -q rich asyncio 2>nul
if %errorlevel% neq 0 (
    echo    ⚠️  Installing dependencies...
    pip install rich asyncio
)
echo    ✅ Dependencies ready

echo.
echo    [3/3] 🚀 Starting Autonomous Mode...
echo.

:: Create directories if needed
if not exist data mkdir data
if not exist logs mkdir logs

echo    ════════════════════════════════════════════════════════════
echo    🎉 MR.VERMA AUTONOMOUS is starting!
echo    ════════════════════════════════════════════════════════════
echo.
echo    📋 What will happen automatically:
echo       • Platform detection (TRAE, Antigravity, OpenCode, etc.)
echo       • Project analysis and agent assignment
-echo       • Docker infrastructure management
-echo       • VibeCoding mode activation
-echo       • Self-managing workflows
-echo.
echo    ⚡ NO CONFIGURATION NEEDED - Just works!
echo.
echo    Press any key to start autonomous operation...
echo.
pause >nul

:: Launch autonomous system
python unified\mrverma_autonomous.py

:: Cleanup
call venv\Scripts\deactivate.bat 2>nul
echo.
echo    👋 Autonomous system stopped.
pause
exit /b 0
