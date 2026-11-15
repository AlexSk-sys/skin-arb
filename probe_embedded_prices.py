import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/json",
}

URLS = [
    ("Tradeit dota2", "https://tradeit.gg/dota2"),
    ("Tradeit rust", "https://tradeit.gg/rust"),
    ("SkinsMonkey dota2", "https://skinsmonkey.com/dota2"),
    ("ShadowPay dota2", "https://shadowpay.com/dota2"),
    ("Loot.farm dota2", "https://loot.farm/?game=dota2"),
    ("Swap.gg dota2", "https://swap.gg/dota2/trade"),
    ("White.Market rust", "https://white.market/rust"),
]

MARKERS = ("market_hash_name", '"price"', "__NEXT_DATA__", "__NUXT_DATA__", "__INITIAL_STATE__", "item_name")

for name, url in URLS:
    try:
        r = requests.get(url, headers=UA, timeout=30)
        text = r.text
        found = {m: text.count(m) for m in MARKERS if m in text}
        print(f"{name:<20} {r.status_code} {len(text):>9}b  {found or '—'}")
    except Exception as e:  # noqa: BLE001
        print(f"{name:<20} ERR {type(e).__name__}")
