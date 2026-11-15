import json

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
BASE = "https://lis-skins.stoplight.io/api/v1/projects/288247"

CANDIDATES = [
    f"{BASE}/nodes",
    f"{BASE}/branches/main/nodes",
    f"{BASE}/export?format=oas3",
    f"{BASE}/export?format=json",
]

for url in CANDIDATES:
    try:
        r = requests.get(url, headers=UA, timeout=30)
        print(f"=== {r.status_code} {url} {r.headers.get('content-type','')[:24]} {len(r.content)}")
        print(r.text[:500].replace("\n", " "))
    except Exception as e:  # noqa: BLE001
        print(f"=== ERR {url} {type(e).__name__}")
