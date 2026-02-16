@echo off
chcp 65001 >nul
title MR.VERMA Document & Code Generation
color 0B
cls

echo.
echo    ╔═══════════════════════════════════════════════════════════╗
echo    ║                                                           ║
echo    ║    MR.VERMA DOCUMENT ^& CODE GENERATION SYSTEM           ║
echo    ║                                                           ║
echo    ║    📄 DOCX  📊 PPTX  📈 XLSX  🗄️ SQLite  🔢 Vectors       ║
echo    ║                                                           ║
echo    ╚═══════════════════════════════════════════════════════════╝
echo.

:: Set working directory
cd /d "%~dp0"

echo    [1/3] Checking dependencies...

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    ❌ Python not found. Please install Python 3.9+
    pause
    exit /b 1
)
echo    ✅ Python ready

:: Setup environment
if not exist venv (
    python -m venv venv
    echo    ✅ Virtual environment created
)

call venv\Scripts\activate.bat

echo.
echo    [2/3] Installing document generation libraries...
pip install -q python-docx python-pptx openpyxl numpy rich 2>nul
if %errorlevel% neq 0 (
    echo    ⚠️  Installing libraries...
    pip install python-docx python-pptx openpyxl numpy rich
)
echo    ✅ Libraries ready

echo.
echo    [3/3] Creating output directories...
if not exist output\documents mkdir output\documents
if not exist data mkdir data
echo    ✅ Directories ready

echo.
echo    ═══════════════════════════════════════════════════════════
echo    🚀 Starting Document Generation System...
echo    ═══════════════════════════════════════════════════════════
echo.

:: Run document generation demo
python unified\document_generation.py

echo.
echo    ✅ Document generation complete!
echo    📁 Check 'output/documents/' for generated files
echo.
pause
exit /b 0
