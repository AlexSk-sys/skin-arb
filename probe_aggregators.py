import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

TARGETS = [
    ("steamanalyst", "https://csgo.steamanalyst.com/"),
    ("skinsearch", "https://skinsearch.com/"),
    ("csgoskins", "https://csgoskins.gg/"),
]

for name, url in TARGETS:
    print(f"=== {name} {url}")
    try:
        r = requests.get(url, headers=UA, timeout=25)
        print("  status", r.status_code, "bytes", len(r.content))
        hints = set()
        for pat in (r'href="([^"]*api[^"]*)"', r'(https://api\.[a-z0-9.-]+)', r'"(/api/[a-z0-9/_-]+)"'):
            hints |= set(re.findall(pat, r.text, re.I))
        for h in sorted(hints)[:15]:
            print("   hint:", h[:110])
    except Exception as e:  # noqa: BLE001
        print("  ERR", type(e).__name__, str(e)[:80])

print("\n=== candidate API hosts ===")
for u in (
    "https://api.steamanalyst.com/",
    "https://api.steamanalyst.com/v1/prices",
    "https://csgo.steamanalyst.com/api/prices",
    "https://api.skinsearch.com/",
    "https://skinsearch.com/api/prices",
):
    try:
        r = requests.get(u, headers=UA, timeout=15)
        print(f"{r.status_code} {u} | {r.text[:90].replace(chr(10), ' ')}")
    except Exception as e:  # noqa: BLE001
        print(f"ERR {u} | {type(e).__name__}")
