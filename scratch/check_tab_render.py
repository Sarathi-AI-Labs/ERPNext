import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()

pos = text.find('role="tab"')
if pos != -1:
    print(text[pos-100:pos+300])

pos2 = text.find('workspaceIcon')
if pos2 != -1:
    print("\nworkspaceIcon found:")
    print(text[pos2-50:pos2+300])
