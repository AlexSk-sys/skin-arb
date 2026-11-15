import re
from collections import deque
from pathlib import Path

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
BASE = "https://white.market"
TARGETS = ("InventoryMy", "MarketList", "MarketNewMultiple", "WalletBalance", "InstantSellList")

html = requests.get(BASE + "/", headers=UA, timeout=30).text
js = set(re.findall(r'(?:src|href)="([^"]+\.js[^"]*)"', html))
queue = deque(s if s.startswith("http") else BASE + ("" if s.startswith("/") else "/") + s for s in js)
seen = set()
found: dict[str, str] = {}

while queue and len(seen) < 80 and len(found) < len(TARGETS):
    url = queue.popleft()
    if url in seen:
        continue
    seen.add(url)
    try:
        body = requests.get(url, headers=UA, timeout=30).text
    except Exception:  # noqa: BLE001
        continue
    for name in TARGETS:
        if name in found:
            continue
        m = re.search(rf"gql`\s*(?:query|mutation)\s+{name}\b(.*?)`", body, re.S)
        if m:
            found[name] = f"{name}{m.group(1)}"
    for m in re.findall(r'["\'](/_next/static/chunks/[A-Za-z0-9/_.-]+\.js)["\']', body):
        queue.append(BASE + m)

out = Path(__file__).resolve().parent / "white_queries.txt"
with out.open("w", encoding="utf-8") as f:
    for name, q in found.items():
        f.write(f"### {name}\n{q}\n\n")
print("extracted:", list(found))
print("saved to", out)
