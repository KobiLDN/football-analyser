@echo off
cd /d "G:\My Drive\coding\ai\football-analyser"

echo Build fixtures.json + fixtures_research_needed_prompt.txt for a
echo DeepSeek research batch. The prompt file is ready to paste:
echo your fixtures, the schema and the canonical team list are all
echo baked in — copy it straight into DeepSeek (web search ON).
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
