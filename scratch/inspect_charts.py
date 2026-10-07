with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()

import re

matches = re.finditer(r'class=["\'][^"\']*sd-chart[^"\']*["\']', text)
for m in list(matches)[:10]:
    start = max(0, m.start() - 50)
    end = min(len(text), m.end() + 200)
    print("MATCH:")
    print(text[start:end])
    print('---')

matches2 = re.finditer(r'class=["\'][^"\']*sd-pipeline[^"\']*["\']', text)
for m in list(matches2)[:5]:
    start = max(0, m.start() - 50)
    end = min(len(text), m.end() + 200)
    print("PIPELINE MATCH:")
    print(text[start:end])
    print('---')
