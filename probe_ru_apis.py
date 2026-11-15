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


def crawl(base: str, page: str, limit: int = 30) -> set[str]:
    html = requests.get(base + page, headers=UA, timeout=30).text
    js = set(re.findall(r'(?:src|href)="([^"]+\.js[^"]*)"', html))
    queue = deque(
        s if s.startswith("http") else base + ("" if s.startswith("/") else "/") + s for s in js
    )
    seen, found = set(), set()
    while queue and len(seen) < limit:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        try:
            body = requests.get(url, headers=UA, timeout=30).text
        except Exception:  # noqa: BLE001
            continue
        found |= set(re.findall(r'["\'`](/?api/[A-Za-z0-9/_.-]{2,60})["\'`]', body))
        found |= set(re.findall(r'["\'`](https://api\.[a-z0-9.-]+[A-Za-z0-9/_.-]*)["\'`]', body))
        for m in re.findall(r'from"\./([A-Za-z0-9_-]+\.js)"', body):
            queue.append(base + "/_nuxt/" + m)
        for m in re.findall(r'import\("\./([A-Za-z0-9_-]+\.js)"\)', body):
            queue.append(base + "/_nuxt/" + m)
    return found


for name, base, page in (
    ("ShadowPay", "https://shadowpay.com", "/"),
    ("CS.MONEY", "https://cs.money", "/"),
    ("Loot.farm", "https://loot.farm", "/"),
):
    try:
        paths = crawl(base, page)
        print(f"=== {name}: {len(paths)} paths")
        for p in sorted(paths)[:25]:
            print("  ", p[:100])
    except Exception as e:  # noqa: BLE001
        print(f"=== {name} ERR {type(e).__name__}")

print("\n=== ShadowPay direct API guesses ===")
for u in (
    "https://api.shadowpay.com/api/v1/items",
    "https://api.shadowpay.com/api/v1/skins",
    "https://api.shadowpay.com/api/v1/market/items",
    "https://shadowpay.com/api/v1/items",
):
    try:
        r = requests.get(u, headers=UA, timeout=20)
        print(f"{r.status_code} {u[:70]:<70} {r.text[:80]}")
    except Exception as e:  # noqa: BLE001
        print(f"ERR {u[:70]} {type(e).__name__}")
