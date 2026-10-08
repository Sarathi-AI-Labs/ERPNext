import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()

pos = text.find('data-accounting-cards')
while pos != -1:
    print('Match at', pos)
    print(text[pos-100:pos+1500])
    print('='*50)
    pos = text.find('data-accounting-cards', pos+1)

pos2 = text.find('data-subcontracting-cards')
while pos2 != -1:
    print('Subcontracting Match at', pos2)
    print(text[pos2-100:pos2+1500])
    print('='*50)
    pos2 = text.find('data-subcontracting-cards', pos2+1)
