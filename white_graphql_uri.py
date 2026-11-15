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

while queue and len(seen) < 40:
    url = queue.popleft()
    if url in seen:
        continue
    seen.add(url)
    try:
        body = requests.get(url, headers=UA, timeout=30).text
    except Exception:  # noqa: BLE001
        continue
    for m in re.finditer(r"graphql", body, re.I):
        i = m.start()
        snippet = body[max(0, i - 200): i + 200]
        if "http" in snippet or "uri" in snippet.lower() or "url" in snippet.lower():
            print(f"[{url[-40:]}] ...{snippet.replace(chr(10), ' ')}...")
            print("-" * 60)
    for m in re.findall(r'["\'](/_next/static/chunks/[A-Za-z0-9/_.-]+\.js)["\']', body):
        queue.append(BASE + m)
