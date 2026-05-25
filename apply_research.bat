@echo off
cd /d "G:\My Drive\coding\ai\football-analyser\football-analyserDEV"

echo Apply DeepSeek research from research.json to index.html
echo (and commit + push to the current branch).
echo.

python apply_research.py
pause
