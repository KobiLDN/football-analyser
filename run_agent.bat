@echo off
cd /d "G:\My Drive\coding\ai\football-analyser\football-analyserDEV"

echo Testing Understat xG fetch...
python -c "from understatapi import UnderstatClient; uc=UnderstatClient(); m=uc.team('Arsenal').get_match_data('2025'); uc.close(); played=[x for x in m if x.get('isResult')][-1]; print('  xG OK - last match xG:', played['xG'], 'xGA:', played['xGA'])"
echo.

echo Running agent...
python agent.py
pause
