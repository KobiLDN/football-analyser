@echo off
cd /d "G:\My Drive\coding\ai\football-analyser"

echo Auto-research fixture stubs via OpenRouter (deepseek:online).
echo Requires OPENROUTER_API_KEY — set in your shell or in a .env file.
echo.
echo No args   = stubs in next 7 days, all leagues, cap 5
echo.
echo Examples:
echo   auto_research.bat --league pl
echo   auto_research.bat --league worldcup --days -1 --max 30
echo   auto_research.bat --days -1 --max 25 --offset 25    (batch 2)
echo   auto_research.bat --no-apply   (write research.json, don't push)
echo   auto_research.bat --dry-run    (show prompt, no API call)
echo.

python auto_research.py %*
pause
