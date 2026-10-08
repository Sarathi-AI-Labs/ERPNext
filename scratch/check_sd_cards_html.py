with open('sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.html', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'sd-cards' in l:
        print(f"Line {i+1}: {l.strip()}")
