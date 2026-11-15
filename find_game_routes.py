import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

SITES = [
    ("Tradeit.gg", "https://tradeit.gg/"),
    ("SkinsMonkey", "https://skinsmonkey.com/"),
    ("ShadowPay", "https://shadowpay.com/"),
    ("White.Market", "https://white.market/"),
]

for name, url in SITES:
    try:
        r = requests.get(url, headers=UA, timeout=25)
        links = set(re.findall(r'href="([^"]+)"', r.text))
        hits = [l for l in links if any(k in l.lower() for k in ("dota", "tf2", "rust", "team-fortress"))]
        print(f"=== {name}: {len(hits)} game links")
        for h in sorted(hits)[:12]:
            print("  ", h[:120])
    except Exception as e:  # noqa: BLE001
        print(f"=== {name} ERR {type(e).__name__}")
