@echo off
title AI Digital Signature - Launcher

echo ===================================================
echo     KHOI DONG HE THONG AI DIGITAL SIGNATURE
echo ===================================================
echo.

echo [1/2] Dang khoi dong Giao dien Web (React)...
start "AI-ECDSA Web Dashboard" cmd /c "cd /d "%~dp0ai-dashboard" && npm install && npm run dev"

echo [2/2] Dang khoi dong Backend API (Python Flask)...
start "AI-ECDSA Backend API" cmd /c "cd /d "%~dp0AI_DigitalSignature" && python api_server.py"

echo.
echo Dang doi may chu khoi dong...
timeout /t 3 >nul

echo Mo trinh duyet mac dinh...
start http://localhost:5173

echo.
echo ===================================================
echo Dang khoi dong ung dung...
echo - Giao dien ung dung se hien thi tren trinh duyet (localhost:5173).
echo - Backend API chay ngam o cong 5000.
echo - Luu y: Giu nguyen 2 cua so den (terminal) de he thong hoat dong.
echo ===================================================
echo.

echo Bam phim bat ky de dong cua so nay...
pause >nul
