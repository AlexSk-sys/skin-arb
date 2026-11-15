import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

SITES = [
    ("Loot.farm", "https://loot.farm/"),
    ("Swap.gg", "https://swap.gg/"),
    ("ShadowPay", "https://shadowpay.com/"),
    ("Tradeit.gg", "https://tradeit.gg/"),
    ("SkinsMonkey", "https://skinsmonkey.com/"),
    ("White.Market", "https://white.market/"),
    ("Waxpeer", "https://waxpeer.com/"),
]

KEYS = ["withdraw", "вывод", "payout", "usdt", "crypto", "сбп", "sbp", "card", "карт", "dota"]

for name, url in SITES:
    try:
        r = requests.get(url, headers=UA, timeout=20)
        text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).lower()
        found = [k for k in KEYS if k in text]
        print(f"{name:<13} {r.status_code}  {', '.join(found) if found else '—'}")
    except Exception as e:  # noqa: BLE001
        print(f"{name:<13} ERR {type(e).__name__}")
