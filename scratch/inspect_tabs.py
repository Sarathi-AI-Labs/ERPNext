import re

with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    text = f.read()

# Find accounting tabs
for m in re.finditer(r'acc_tabs|accTabs|accountingTabs|subcontractingTabs', text, re.IGNORECASE):
    idx = m.start()
    print("--- MATCH AT", idx, "---")
    print(text[idx-20:idx+400])

# Find Frappe charts or charts in sarathi_dashboard.js
print("--- CHARTS IN CONTROL TOWER ---")
charts = re.findall(r'new\s+frappe\.Chart\([^,]+,\s*\{', text)
print(f"Found {len(charts)} frappe.Chart instantiations")

chart_blocks = re.findall(r'colors\s*:\s*\[[^\]]+\]', text)
for cb in chart_blocks[:10]:
    print(cb)
