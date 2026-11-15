import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

SITES = [
    ("Waxpeer", "https://waxpeer.com/"),
    ("CS.MONEY", "https://cs.money/"),
    ("Loot.farm", "https://loot.farm/"),
    ("White.Market", "https://white.market/"),
    ("DMarket", "https://dmarket.com/"),
    ("SkinsBack", "https://skinsback.com/"),
    ("TM Market", "https://tm.market/"),
]

KEYS = ["dota", "usdt", "сбп", "sbp", "card", "карт", "crypto", "payeer", "юmoney", "yoomoney", "qiwi", "mir"]

for name, url in SITES:
    try:
        r = requests.get(url, headers=UA, timeout=20)
        text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).lower()
        found = [k for k in KEYS if k in text]
        print(f"{name:<14} {r.status_code}  {', '.join(found) if found else '—'}")
    except Exception as e:  # noqa: BLE001
        print(f"{name:<14} ERR {type(e).__name__}")
