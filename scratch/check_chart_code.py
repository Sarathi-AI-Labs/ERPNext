with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()

import re

# find renderChart or chart rendering function
pos = text.find('renderChart')
if pos != -1:
    print("Found renderChart:")
    print(text[pos:pos+2500])
else:
    # search for chart-
    for m in re.finditer(r'render\w*Chart\w*\(', text):
        idx = m.start()
        print(text[idx:idx+400])
