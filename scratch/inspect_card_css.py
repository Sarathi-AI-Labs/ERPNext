import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css', encoding='utf-8') as f:
    text = f.read()

pos = text.find('.sd-accounting-main-card')
print(text[pos:pos+3000])
