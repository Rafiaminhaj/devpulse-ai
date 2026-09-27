@echo off
cd /d "C:\Users\adiqu\.gemini\antigravity\scratch\devpulse-ai"
echo ========================================================
echo         DevPulse AI — 1-Click GitHub Push Script
echo ========================================================
echo.
echo Current Directory: %CD%
git remote remove origin >nul 2>&1
git remote add origin https://github.com/Rafiaminhaj/devpulse-ai.git
git branch -M main
git push -u origin main
echo.
echo ========================================================
echo SUCCESS! Your DevPulse AI codebase is live on GitHub!
echo ========================================================
pause
