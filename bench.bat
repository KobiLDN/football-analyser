@echo off
cd /d "G:\My Drive\coding\ai\football-analyser"

echo Model benchmark — sweeps all models in bench.py MODELS list.
echo You will be prompted to load each model in LM Studio between runs.
echo News is fetched once and cached so every model gets identical input.
echo.

python bench.py --all
pause
