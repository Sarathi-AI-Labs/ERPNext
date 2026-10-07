import urllib.request

urls = [
    ("Owner CSS", "http://localhost:8080/assets/sarathi_owner/css/sarathi_owner_dashboard.css"),
    ("Control Tower CSS", "http://localhost:8080/assets/sarathi_visibility/css/sarathi_dashboard.css"),
    ("Owner Tower Page", "http://localhost:8080/desk/sarathiownertower"),
    ("Control Tower Page", "http://localhost:8080/desk/sarathicontroltower")
]

for label, url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[{label}] -> HTTP {resp.status}, length: {len(data)} bytes")
            if "CSS" in label:
                text = data.decode('utf-8', errors='ignore')
                print(f"    - Fonts imported: {'fonts.googleapis.com' in text}")
                print(f"    - Master Theme found: {'MASTER' in text}")
    except Exception as e:
        print(f"[{label}] -> Error: {e}")
