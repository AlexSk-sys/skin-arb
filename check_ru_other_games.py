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
    ("ShadowPay", "https://shadowpay.com/"),
    ("Market.CSGO", "https://market.csgo.com/ru/"),
    ("White.Market", "https://white.market/"),
    ("Tradeit.gg", "https://tradeit.gg/"),
    ("Swap.gg", "https://swap.gg/"),
    ("SkinsMonkey", "https://skinsmonkey.com/"),
    ("SkinsBack", "https://skinsback.com/"),
    ("CS.MONEY", "https://cs.money/"),
    ("LIS-SKINS", "https://lis-skins.com/"),
]

GAMES = ["dota", "tf2", "rust", "team fortress"]
PAY = ["сбп", "sbp", "мир", "usdt", "crypto", "карт", "card", "юmoney", "yoomoney", "payeer"]

for name, url in SITES:
    try:
        r = requests.get(url, headers=UA, timeout=20)
        text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).lower()
        games = [g for g in GAMES if g in text]
        pays = [p for p in PAY if p in text]
        print(f"{name:<13} {r.status_code}  games: {', '.join(games) or '—':<26} pay: {', '.join(pays) or '—'}")
    except Exception as e:  # noqa: BLE001
        print(f"{name:<13} ERR {type(e).__name__}")
