import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()

pos = text.find('closeSubcontractingView')
if pos != -1:
    print("closeSubcontractingView:")
    print(text[pos:pos+1500])

pos2 = text.find('closeAccountingView')
if pos2 != -1:
    print("closeAccountingView:")
    print(text[pos2:pos2+1500])
