@echo off
cd /d "G:\My Drive\coding\ai\football-analyser\football-analyserDEV"

echo Game-day refresh: resets unplayed fixtures kicking off in the
echo next 2 days (today + tomorrow by default), then re-researches
echo them with the latest news. Pass a different number for a wider
echo window, e.g. "refresh_today.bat 5" for the whole week.
echo.

if "%1"=="" (
    python refresh_today.py --days 2
) else (
    python refresh_today.py --days %1
)
pause
