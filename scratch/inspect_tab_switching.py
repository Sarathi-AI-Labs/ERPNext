import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()

import re

for m in re.finditer(r'data-tab|this\.tab\s*=|switchTab|selectTab|renderTab', text):
    idx = m.start()
    print("Match at", idx, ":")
    print(text[idx-50:idx+250])
    print('---')
