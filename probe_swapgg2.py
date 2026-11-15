import json
import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

for url in ("https://swap.gg/dota2/trade", "https://swap.gg/rust/trade", "https://swap.gg/tf2/trade"):
    try:
        r = requests.get(url, headers=UA, timeout=30)
        print(f"=== {url} {r.status_code} {len(r.content)}")
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.S)
        if m:
            data = json.loads(m.group(1))
            txt = json.dumps(data, ensure_ascii=False)
            print("  NEXT_DATA chars:", len(txt))
            print("  sample:", txt[:300])
        else:
            print("  no NEXT_DATA")
    except Exception as e:  # noqa: BLE001
        print(f"=== {url} ERR {type(e).__name__}")

print("\n=== api path guesses ===")
for path in (
    "/api/v1/items",
    "/api/items/list",
    "/api/market/items",
    "/api/games",
    "/api/config",
    "/api/inventory",
    "/api/v1/market/items",
):
    try:
        r = requests.get("https://swap.gg" + path, headers=UA, timeout=25)
        print(f"{r.status_code} {path:<28} {r.text[:100]}")
    except Exception as e:  # noqa: BLE001
        print(f"ERR {path} {type(e).__name__}")
