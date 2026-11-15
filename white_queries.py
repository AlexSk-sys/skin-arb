import re
from collections import deque

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
BASE = "https://white.market"
html = requests.get(BASE + "/", headers=UA, timeout=30).text
js = set(re.findall(r'(?:src|href)="([^"]+\.js[^"]*)"', html))
queue = deque(s if s.startswith("http") else BASE + ("" if s.startswith("/") else "/") + s for s in js)
seen = set()
hits = 0

while queue and len(seen) < 60 and hits < 12:
    url = queue.popleft()
    if url in seen:
        continue
    seen.add(url)
    try:
        body = requests.get(url, headers=UA, timeout=30).text
    except Exception:  # noqa: BLE001
        continue
    for kw in ("steam_market_hash_name", "marketItems", "items(", "getItems", "price"):
        i = body.find(kw)
        if i >= 0:
            print(f"[{url[-45:]}] {kw}: ...{body[max(0, i-250):i+350].replace(chr(10), ' ')}...")
            print("-" * 70)
            hits += 1
            break
    for m in re.findall(r'["\'](/_next/static/chunks/[A-Za-z0-9/_.-]+\.js)["\']', body):
        queue.append(BASE + m)
