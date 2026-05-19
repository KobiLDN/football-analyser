@echo off
cd /d "G:\My Drive\coding\ai\football-analyser\football-analyserDEV"

echo Game-day refresh: resets only today's unplayed fixtures, then
echo re-researches them with the latest news. Pass an arg for more
echo days, e.g. "refresh_today.bat 2" for today + tomorrow.
echo.

if "%1"=="" (
    python refresh_today.py
) else (
    python refresh_today.py --days %1
)
pause
