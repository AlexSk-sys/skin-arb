import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

URLS = [
    ("Tradeit rust store", "https://tradeit.gg/rust/store"),
    ("Tradeit tf2 store", "https://tradeit.gg/tf2/store"),
    ("ShadowPay dota", "https://shadowpay.com/dota-2-items"),
    ("ShadowPay rust", "https://shadowpay.com/rust-items"),
    ("SkinsMonkey dota", "https://skinsmonkey.com/dota-2"),
    ("White.Market rust", "https://white.market/rust"),
]

MARKERS = ("market_hash_name", '"price"', "__NEXT_DATA__", "__NUXT_DATA__", '"name"', "USDT")

for name, url in URLS:
    try:
        r = requests.get(url, headers=UA, timeout=30)
        text = r.text
        found = {m: text.count(m) for m in MARKERS if m in text}
        print(f"{name:<20} {r.status_code} {len(text):>9}b  {found or '—'}")
        if found:
            i = text.find('"price"')
            if i > 0:
                print("   sample:", text[max(0, i-150):i+150].replace("\n", " ")[:300])
    except Exception as e:  # noqa: BLE001
        print(f"{name:<20} ERR {type(e).__name__}")
