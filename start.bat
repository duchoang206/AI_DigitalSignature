@echo off
title AI Digital Signature - Launcher

echo ===================================================
echo     KHOI DONG HE THONG AI DIGITAL SIGNATURE
echo ===================================================
echo.

echo [1/2] Dang khoi dong Backend API (Python Flask)...
start "AI-ECDSA Backend API" cmd /c "cd /d "%~dp0AI_DigitalSignature" && python api_server.py"

echo [2/2] Dang khoi dong Giao dien Dashboard (React)...
start "AI Dashboard Frontend" cmd /c "cd /d "%~dp0ai-dashboard" && npm run dev"

echo.
echo ===================================================
echo Dang mo trinh duyet Web...
echo - Backend API chay o: http://localhost:5000
echo - Giao dien se mo o: http://localhost:5173
echo ===================================================
echo.

:: Doi 3 giay de server kip khoi dong
timeout /t 3 /nobreak >nul

:: Mo trinh duyet mac dinh toi cong 5173
start http://localhost:5173

echo Bam phim bat ky de dong cua so khoi dong nay...
pause >nul
