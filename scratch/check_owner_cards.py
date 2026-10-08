with open('sarathi_owner/sarathi_owner/public/css/sarathi_owner_dashboard.css', encoding='utf-8') as f:
    text = f.read()

import re

card_classes = re.findall(r'\.sod-[a-z0-9_-]*card[a-z0-9_-]*', text)
print("Owner dashboard card classes:", set(card_classes))
