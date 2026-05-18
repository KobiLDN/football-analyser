import re
import sys

STUB = "summary: 'Pending deep research.'"
HTML_FILE = "index.html"

with open(HTML_FILE, "r", encoding="utf-8") as f:
    html = f.read()

# Match summary value including escaped apostrophes (e.g. player\'s)
SUMMARY_RE = re.compile(r"summary:\s*'((?:[^'\\]|\\.)*?)'")

count = 0
offset = 0
while True:
    null_idx = html.find("result: null", offset)
    if null_idx == -1:
        break
    window_end = min(null_idx + 3000, len(html))
    m = SUMMARY_RE.search(html, null_idx, window_end)
    if m and m.group(1) != "Pending deep research.":
        html = html[:m.start()] + STUB + html[m.end():]
        count += 1
    offset = null_idx + 1

stubs = html.count(STUB)
print(f"Reset {count} fixtures, total stubs: {stubs}")

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html)
print("Done.")
