import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

SITES = [
    ("Market.CSGO", "https://market.csgo.com/en/"),
    ("Market.CSGO wallet", "https://market.csgo.com/en/wallet"),
    ("LIS-SKINS", "https://lis-skins.com/"),
    ("CS.MONEY", "https://cs.money/"),
    ("ShadowPay", "https://shadowpay.com/"),
    ("White.Market", "https://white.market/"),
    ("Skin.land", "https://skin.land/"),
    ("SkinsBack", "https://skinsback.com/"),
    ("Waxpeer", "https://waxpeer.com/"),
]

KEYWORDS = ["СБП", "SBP", "МИР", "Mir", "Visa", "Mastercard", "карт", "card", "USDT", "crypto", "bank"]

for name, url in SITES:
    try:
        r = requests.get(url, headers=UA, timeout=20)
        text = re.sub(r"<[^>]+>", " ", r.text)
        text = re.sub(r"\s+", " ", text)
        found = [k for k in KEYWORDS if k.lower() in text.lower()]
        print(f"{name:<20} {r.status_code}  keywords: {', '.join(found) if found else '—'}")
    except Exception as e:  # noqa: BLE001
        print(f"{name:<20} ERR {type(e).__name__}")
