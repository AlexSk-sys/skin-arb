import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}

CANDIDATES = [
    ("lis-skins.com", "https://lis-skins.com/market_export_json/api_csgo_full.json"),
    ("lis-skins.ru", "https://lis-skins.ru/market_export_json/api_csgo_full.json"),
    ("cs.money prices", "https://api.cs.money/api/v1/prices"),
    ("cs.money load", "https://api.cs.money/api/v1/load"),
    ("white.market", "https://api.white.market/api/v1/prices"),
    ("white.market alt", "https://white.market/api/prices"),
    ("shadowpay", "https://api.shadowpay.com/api/prices"),
    ("shadowpay v1", "https://api.shadowpay.com/api/v1/prices"),
]

for name, url in CANDIDATES:
    try:
        r = requests.get(url, headers=UA, timeout=45)
        ct = r.headers.get("content-type", "")[:20]
        print(f"{name:<16} {r.status_code} {ct:<20} {len(r.content):>9}  {r.text[:90].replace(chr(10), ' ')}")
    except Exception as e:  # noqa: BLE001
        print(f"{name:<16} ERR {type(e).__name__}: {str(e)[:70]}")
