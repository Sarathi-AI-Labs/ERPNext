import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()

import re

selectors = set()
for m in re.finditer(r'el\(\s*["\']([^"\']+)["\']\s*\)|querySelector(?:All)?\(\s*["\']([^"\']+)["\']\s*\)', text):
    s = m.group(1) or m.group(2)
    selectors.add(s)

print(f"Total distinct selectors in sarathi_dashboard.js: {len(selectors)}")
for s in sorted(selectors):
    print(" -", s)
