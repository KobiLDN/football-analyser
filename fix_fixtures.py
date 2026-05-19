import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix Mönchengladbach — corrupted to 'M\\' in the JS string
# In the file the literal bytes are: home: 'M\\', (two backslashes then quote)
old_name = "home: 'M\\\\', away: 'Hoffenheim'"
new_name = "home: 'Mönchengladbach', away: 'Hoffenheim'"
if old_name in html:
    html = html.replace(old_name, new_name)
    print("Fixed: Mönchengladbach name")
else:
    print("WARNING: Mönchengladbach pattern not found")

# 2. Mark Gladbach 4-0 Hoffenheim result
idx = html.find(new_name)
if idx >= 0:
    chunk = html[idx:idx+200]
    if 'result: null' in chunk:
        html = html[:idx] + chunk.replace('result: null', "'4-0'".join(["result: ", ""]), 1) + html[idx+200:]
        print("Fixed: Gladbach result 4-0")

# 3. Fix Fulham vs Newcastle — day still Unknown after earlier attempt
old_day = "day: 'Unknown',\n        home: 'Fulham'"
new_day = "day: 'Sunday 24 May',\n        home: 'Fulham'"
if old_day in html:
    html = html.replace(old_day, new_day)
    print("Fixed: Fulham day")
else:
    print("Fulham day already fixed or pattern not found")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = html.match if hasattr(html, 'match') else None
import re
m = re.search(r"const LEAGUES = (\[[\s\S]*?\]);", html)
leagues = eval(m.group(1))
for l in leagues:
    for f in l['fixtures']:
        if 'nchengladbach' in f.get('home', ''):
            print(f"Gladbach: home={f['home']} result={f['result']}")
        if f.get('home') == 'Fulham':
            print(f"Fulham: day={f['day']}")
