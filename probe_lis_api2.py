import re

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
URL = "https://api.lis-skins.com/v1/market/buy"
BODY = {"item_id": 583793166, "price": 4.62}

HEADERS = {
    "X-API-KEY": "test",
    "Authorization": "Bearer test",
    "api-key": "test",
    "Api-Key": "test",
    "X-Api-Key": "test",
}

for name, value in HEADERS.items():
    try:
        r = requests.post(URL, headers={**UA, name: value}, json=BODY, timeout=25)
        print(f"{name:<14} {r.status_code} {r.text[:180].replace(chr(10), ' ')}")
    except Exception as e:  # noqa: BLE001
        print(f"{name:<14} ERR {type(e).__name__}")

print("\n--- docs page hints ---")
try:
    r = requests.get(
        "https://lis-skins.stoplight.io/docs/lis-skins/dzq78x3edc19r-api-overview",
        headers={**UA, "Accept": "text/html"},
        timeout=30,
    )
    print("status", r.status_code, "bytes", len(r.content))
    for pat in ("api_key", "api-key", "X-API", "Authorization", "market/buy", "item_id"):
        hits = re.findall(r".{60}" + pat + r".{80}", r.text, re.I)
        if hits:
            print(f"[{pat}] {hits[0][:180]}")
except Exception as e:  # noqa: BLE001
    print("docs ERR", type(e).__name__)
