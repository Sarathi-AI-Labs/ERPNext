with open('sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css', encoding='utf-8') as f:
    text = f.read()

import re

selectors_to_check = [
    'sd-donut-chart',
    'sd-pipeline',
    'sd-bar',
    'sd-chart-grid',
    'sd-sub-',
    'sd-acc-',
    'sd-pagination',
    'sd-breadcrumb',
    'sd-project-summary'
]

for s in selectors_to_check:
    matches = [m.start() for m in re.finditer(re.escape(s), text)]
    print(f"Selector pattern '{s}': {len(matches)} occurrences")
