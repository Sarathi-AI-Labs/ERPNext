import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()

pos = text.find('chart(c) {')
if pos != -1:
    print("\n--- FOUND chart(c) ---")
    print(text[pos:pos+2000])
