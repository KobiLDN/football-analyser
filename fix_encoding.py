"""
Fix double-encoded UTF-8 in index.html caused by PowerShell's Set-Content
reading the file as CP1252 then writing back as UTF-8.

The reverse: for each run of non-ASCII chars, try encoding as CP1252
then decoding as UTF-8. If it round-trips cleanly, replace with the result.
"""

with open('index.html', 'rb') as f:
    raw = f.read()

# Remove UTF-8 BOM if present
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]
    print("Removed UTF-8 BOM")

text = raw.decode('utf-8')

fixed = []
i = 0
changes = 0

while i < len(text):
    c = text[i]
    if ord(c) > 127:
        # Try to collect a run of chars that encode cleanly as CP1252
        j = i
        cp_bytes = b''
        while j < len(text) and ord(text[j]) > 127:
            try:
                cp_bytes += text[j].encode('cp1252')
                j += 1
            except (UnicodeEncodeError, UnicodeDecodeError):
                break
        if cp_bytes:
            try:
                decoded = cp_bytes.decode('utf-8')
                # Only accept if it produces fewer, more meaningful chars
                if len(decoded) < (j - i):
                    fixed.append(decoded)
                    changes += 1
                    i = j
                    continue
            except (UnicodeDecodeError, ValueError):
                pass
    fixed.append(c)
    i += 1

result = ''.join(fixed)
print(f"Fixed {changes} sequences")

# Write back as UTF-8 without BOM
with open('index.html', 'w', encoding='utf-8', newline='') as f:
    f.write(result)
print("Written as UTF-8 (no BOM)")

# Verify key strings
checks = [
    ('–', 'en dash'),
    ('·', 'middle dot'),
    ('â€"', 'garbled en dash'),
    ('Â·', 'garbled middle dot'),
]
for char, name in checks:
    count = result.count(char)
    print(f"  '{char}' ({name}): {count} occurrences")
