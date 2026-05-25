@echo off
cd /d "G:\My Drive\coding\ai\football-analyser\football-analyserDEV"

echo Build fixtures.json — a list of fixtures to upload to DeepSeek
echo alongside research.template.md.
echo.
echo No args   = upcoming unplayed fixtures, next 7 days, all leagues, cap 20
echo Args      = passed through to make_fixtures_list.py
echo.
echo Examples:
echo   make_fixtures.bat                           (default)
echo   make_fixtures.bat --league pl               (PL only)
echo   make_fixtures.bat --league worldcup --days 14 --max 30
echo   make_fixtures.bat --stubs-only --days -1 --max 100  (every remaining stub)
echo.

python make_fixtures_list.py %*
pause
