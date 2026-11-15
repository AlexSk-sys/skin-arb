import re
from collections import deque

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

SITES = [
    ("CS.MONEY", "https://cs.money", "/"),
    ("Swap.gg", "https://swap.gg", "/"),
    ("Loot.farm", "https://loot.farm", "/"),
    ("Tradeit.gg", "https://tradeit.gg", "/"),
    ("SkinsMonkey", "https://skinsmonkey.com", "/"),
    ("Skin.land", "https://skin.land", "/"),
    ("CS.Deals", "https://cs.deals", "/"),
    ("Mannco.store", "https://mannco.store", "/"),
]

for name, base, page in SITES:
    try:
        r = requests.get(base + page, headers=UA, timeout=25)
    except Exception as e:  # noqa: BLE001
        print(f"=== {name}: homepage ERR {type(e).__name__}")
        continue
    html = r.text
    js = set(re.findall(r'(?:src|href)="([^"]+\.js[^"]*)"', html))
    queue = deque(
        s if s.startswith("http") else base + ("" if s.startswith("/") else "/") + s for s in js
    )
    seen, hosts, paths = set(), set(), set()
    while queue and len(seen) < 18:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        try:
            body = requests.get(url, headers=UA, timeout=25).text
        except Exception:  # noqa: BLE001
            continue
        hosts |= set(re.findall(r'["\'`](https://api\.[a-z0-9.-]+)', body))
        hosts |= set(re.findall(r'["\'`](https://[a-z0-9.-]*graphql[a-z0-9./-]*)', body))
        paths |= set(re.findall(r'["\'`](/api/[A-Za-z0-9/_.-]{2,50})["\'`]', body))
        for m in re.findall(r'["\'](/_next/static/chunks/[A-Za-z0-9/_.-]+\.js)["\']', body):
            queue.append(base + m)
        for m in re.findall(r'["\'](/assets/[A-Za-z0-9/_.-]+\.js)["\']', body):
            queue.append(base + m)
    print(f"=== {name}: {r.status_code}, js {len(seen)}")
    if hosts:
        print("  hosts:", sorted(hosts)[:8])
    if paths:
        print("  paths:", sorted(paths)[:12])
