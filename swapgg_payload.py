import json
import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
html = requests.get("https://swap.gg/dota2/trade", headers=UA, timeout=30).text
m = re.search(
    r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', html, re.S
)
print("found:", bool(m))
if not m:
    raise SystemExit(1)
raw = m.group(1)
print("payload chars:", len(raw))
for kw in ("Urushin", "Whisky", "Genuine Skittering", "price", "\"name\""):
    i = raw.find(kw)
    print(f"[{kw}] idx={i}")
    if i >= 0:
        print("  ", raw[max(0, i - 200): i + 300].replace("\n", " ")[:480])

try:
    data = json.loads(raw)
    print("\ntop type:", type(data), "len:", len(data) if isinstance(data, list) else "-")
    print("first 3:", json.dumps(data[:3], ensure_ascii=False)[:500])
except json.JSONDecodeError as exc:
    print("json error:", exc)
