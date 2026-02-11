@echo off
title STARTING VERMA SYSTEM...
color 0A
echo ===================================================
echo      STARTING AGENT LIGHTNING LOCAL SYSTEM
echo ===================================================
echo.
cd /d "e:\ABHINAV\MR.VERMA\agent-lightning-local"
echo [1/3] Launching Docker Containers...
docker compose up -d
echo.
echo [2/3] Checking Status...
docker ps
echo.
echo [3/3] DONE! System is live.
echo.
echo Dashboard: http://localhost:8551
echo Assistant: http://localhost:8550
echo.
pause
