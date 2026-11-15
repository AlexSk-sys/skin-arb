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
seen, paths = set(), set()

while queue and len(seen) < 60:
    url = queue.popleft()
    if url in seen:
        continue
    seen.add(url)
    try:
        body = requests.get(url, headers=UA, timeout=30).text
    except Exception:  # noqa: BLE001
        continue
    paths |= set(re.findall(r'["\'`](/api/[A-Za-z0-9/_.-]{2,60})["\'`]', body))
    paths |= set(re.findall(r'["\'`](https://api\.[a-z0-9.-]+[A-Za-z0-9/_.-]*)["\'`]', body))
    for m in re.findall(r'["\'](/_next/static/chunks/[A-Za-z0-9/_.-]+\.js)["\']', body):
        queue.append(BASE + m)

print(f"scanned {len(seen)} js files")
for p in sorted(paths)[:50]:
    print("  ", p[:120])
