@echo off
cd /d "G:\My Drive\coding\ai\football-analyser\football-analyserDEV"

echo Resetting all unplayed fixtures to stub state...
python reset_stubs.py
echo.
pause
