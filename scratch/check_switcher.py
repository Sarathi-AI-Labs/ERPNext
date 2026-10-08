with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()

pos = text.find('switch-owner')
print(text[pos-100:pos+250])
