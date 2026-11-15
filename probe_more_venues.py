import re
from collections import deque

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
}

SITES = [
    ("Buff Market", "https://buff.market", "/"),
    ("White.Market", "https://white.market", "/"),
    ("Tradeit.gg", "https://tradeit.gg", "/"),
    ("SkinsMonkey", "https://skinsmonkey.com", "/"),
    ("Loot.farm", "https://loot.farm", "/"),
    ("Swap.gg", "https://swap.gg", "/"),
]

for name, base, page in SITES:
    try:
        html = requests.get(base + page, headers=UA, timeout=25).text
        low = html.lower()
        games = [g for g in ("dota", "tf2", "rust", "team fortress") if g in low]
        js = set(re.findall(r'(?:src|href)="([^"]+\.js[^"]*)"', html))
        queue = deque(
            s if s.startswith("http") else base + ("" if s.startswith("/") else "/") + s for s in js
        )
        seen, paths = set(), set()
        while queue and len(seen) < 12:
            url = queue.popleft()
            if url in seen:
                continue
            seen.add(url)
            try:
                body = requests.get(url, headers=UA, timeout=25).text
            except Exception:  # noqa: BLE001
                continue
            paths |= set(re.findall(r'["\'`](/api/[A-Za-z0-9/_.-]{2,50})["\'`]', body))
            paths |= set(re.findall(r'["\'`](https://api\.[a-z0-9.-]+)["\'`]', body))
        print(f"{name:<13} {len(html):>8}b games: {', '.join(games) or '—':<22} api: {sorted(paths)[:6]}")
    except Exception as e:  # noqa: BLE001
        print(f"{name:<13} ERR {type(e).__name__}")
