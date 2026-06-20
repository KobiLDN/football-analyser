@echo off
cd /d "G:\My Drive\coding\ai\football-analyser"

echo Testing Understat xG fetch...
python -c "from agent import fetch_xg; r=fetch_xg('Arsenal','pl'); print('  xG OK:', r) if r else print('  WARNING: xG returned None')"
echo.

echo Running agent...
python agent.py
pause
