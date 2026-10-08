import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()

import re

for sel in ['data-customer-panel', 'data-project-panel', 'data-subcontracting-card-panel', 'data-accounting-card-panel', 'data-kpis', 'data-live-projects']:
    for m in re.finditer(re.escape(sel), text):
        idx = m.start()
        print(f"Selector {sel} in JS:")
        print(text[idx-40:idx+200])
        print('---')
