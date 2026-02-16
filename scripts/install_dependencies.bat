@echo off
setlocal EnableDelayedExpansion

echo ===================================================
echo      MR.VERMA Dependency Installer & Setup
echo ===================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Install Python Dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.unified.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b 1
)
echo [OK] Python dependencies installed.
echo.

:: Check for Docker (for Milvus/Qdrant)
echo [INFO] Checking Docker...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker is installed.
) else (
    echo [WARNING] Docker is NOT installed. Vector databases (Milvus/Qdrant) might require Docker.
)

:: Check for Node.js (Prisma)
echo [INFO] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Node.js is installed.
) else (
    echo [WARNING] Node.js is NOT installed. Prisma integration will not work.
)

:: Check for Java (Telosys)
echo [INFO] Checking Java...
java -version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Java is installed.
) else (
    echo [WARNING] Java is NOT installed. Telosys integration will not work.
)

:: Check for .NET (Fluid)
echo [INFO] Checking .NET SDK...
dotnet --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] .NET SDK is installed.
) else (
    echo [WARNING] .NET SDK is NOT installed. Fluid templates will not work.
)

echo.
echo ===================================================
echo      Installation Complete
echo ===================================================
echo.
echo Please copy .env.example to .env and configure your keys.
echo.
pause
