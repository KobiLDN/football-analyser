@echo off
cd /d "G:\My Drive\coding\ai\football-analyser\football-analyserDEV"

echo Apply DeepSeek research to live site.
echo   Auto-detects input file:
echo     1. Any newer deepseek_json_*.json downloaded into this folder
echo     2. Or research.json if you've pasted JSON manually
echo.
echo Pipeline:
echo   1. Pulls latest dev / main
echo   2. Replaces fixture blocks in index.html (atomic)
echo   3. Commits + pushes to dev
echo   4. Merges dev -^> main, pushes main (live)
echo   5. Archives the input file -^> *.applied
echo.

python apply_research.py
pause
