@echo off
cd /d "G:\My Drive\coding\ai\football-analyser"

echo Resetting all unplayed fixtures to stub state...
python reset_stubs.py
echo.
pause
