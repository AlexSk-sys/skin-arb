import json

import requests

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0",
    "Accept": "application/json",
}

TESTS = [
    ("GET buy", "GET", "https://api.lis-skins.com/v1/market/buy", None),
    ("POST buy empty", "POST", "https://api.lis-skins.com/v1/market/buy", {}),
    ("GET root", "GET", "https://api.lis-skins.com/", None),
    ("GET docs", "GET", "https://api.lis-skins.com/docs", None),
    ("GET openapi", "GET", "https://api.lis-skins.com/openapi.json", None),
    (
        "GET items search",
        "GET",
        "https://api.lis-skins.com/v1/market/items?name=UMP-45%20%7C%20Houndstooth%20(Factory%20New)",
        None,
    ),
]

for label, method, url, body in TESTS:
    try:
        if method == "GET":
            r = requests.get(url, headers=UA, timeout=25)
        else:
            r = requests.post(url, headers=UA, json=body, timeout=25)
        text = r.text[:300].replace("\n", " ")
        print(f"{label:<18} {r.status_code} {r.headers.get('content-type','')[:24]:<24} {text}")
    except Exception as e:  # noqa: BLE001
        print(f"{label:<18} ERR {type(e).__name__}: {str(e)[:80]}")
