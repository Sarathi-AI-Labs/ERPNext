import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()

pos = text.find('class SarathiIndustrialDashboard')
if pos == -1:
    pos = text.find('SarathiIndustrialDashboard =')
if pos == -1:
    pos = text.find('function SarathiIndustrialDashboard')

if pos != -1:
    print(text[pos:pos+2500])
else:
    print("Class definition not found by name, searching 'constructor(':")
    pos = text.find('constructor(')
    print(text[pos:pos+2000])
