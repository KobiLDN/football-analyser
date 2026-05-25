@echo off
cd /d "G:\My Drive\coding\ai\football-analyser\football-analyserDEV"

echo Apply DeepSeek research from research.json to live site.
echo   1. Pulls latest dev / main
echo   2. Replaces the fixture block in index.html
echo   3. Commits + pushes to dev
echo   4. Merges dev -^> main, pushes main (live)
echo   5. Archives research.json -^> research.json.applied
echo.

python apply_research.py
pause
