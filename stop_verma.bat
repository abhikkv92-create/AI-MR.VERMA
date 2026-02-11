@echo off
title STOPPING VERMA SYSTEM...
color 0C
echo ===================================================
echo      STOPPING AGENT LIGHTNING LOCAL SYSTEM
echo ===================================================
echo.
cd /d "e:\ABHINAV\MR.VERMA\agent-lightning-local"
echo [1/2] Stopping Containers...
docker compose down
echo.
echo [2/2] DONE! System is stopped.
echo.
pause
