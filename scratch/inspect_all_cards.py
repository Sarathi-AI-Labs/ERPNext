import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()


print("--- renderAccountingCard ---")
pos = text.find('renderAccountingCard() {')
if pos != -1:
    print(text[pos:pos+1600])

print("\n--- renderSubcontractingCard ---")
pos = text.find('renderSubcontractingCard() {')
if pos != -1:
    print(text[pos:pos+1200])

print("\n--- renderCards (customers & projects) ---")
pos = text.find('renderCards() {')
if pos != -1:
    print(text[pos:pos+1800])
