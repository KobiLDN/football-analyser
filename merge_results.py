"""
One-off script: copy result values from origin/main index.html into DEV index.html.
DEV has full analysis but result: null. Main has stubs but correct result values.
"""
import re

MAIN_HTML = r"G:\My Drive\coding\ai\drawanalyser\index.html"
DEV_HTML  = r"G:\My Drive\coding\ai\drawanalyserDEV\index.html"


def extract_results(html):
    """Return dict of {(home, away): result_str} for all non-null results."""
    results = {}
    fixture_pattern = re.compile(
        r"home:\s*'([^']+)',\s*away:\s*'([^']+)',\s*time:\s*'[^']+',\s*\n?\s*result:\s*'([^']+)'",
        re.DOTALL
    )
    for m in fixture_pattern.finditer(html):
        results[(m.group(1), m.group(2))] = m.group(3)
    return results


def apply_results(dev_html, results):
    """Replace result: null with the actual result for matching fixtures."""
    updated = 0
    for (home, away), result in results.items():
        pattern = re.compile(
            r"(home:\s*'" + re.escape(home) + r"',\s*away:\s*'" + re.escape(away) +
            r"',\s*time:\s*'[^']+',\s*\n?\s*)result:\s*null",
            re.DOTALL
        )
        new_html, count = pattern.subn(r"\g<1>result: '" + result + "'", dev_html)
        if count:
            dev_html = new_html
            updated += 1
            print(f"  Updated result for {home} vs {away}: {result}")
    print(f"\n{updated} results applied.")
    return dev_html


with open(MAIN_HTML, "r", encoding="utf-8") as f:
    main_html = f.read()

with open(DEV_HTML, "r", encoding="utf-8") as f:
    dev_html = f.read()

results = extract_results(main_html)
print(f"Found {len(results)} results in main.\n")

merged = apply_results(dev_html, results)

with open(DEV_HTML, "w", encoding="utf-8") as f:
    f.write(merged)

print("DEV index.html updated.")
