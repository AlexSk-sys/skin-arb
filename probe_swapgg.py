import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
}

print("=== swap.gg pages ===")
for url in ("https://swap.gg/", "https://swap.gg/dota2", "https://swap.gg/api", "https://swap.gg/market"):
    try:
        r = requests.get(url, headers=UA, timeout=25, allow_redirects=True)
        print(f"{r.status_code} {url[:40]:<40} -> {r.url[:60]:<60} {len(r.content)}")
    except Exception as e:  # noqa: BLE001
        print(f"ERR {url[:40]} {type(e).__name__}")

print("\n=== swap.gg API hints ===")
try:
    html = requests.get("https://swap.gg/", headers=UA, timeout=25).text
    js = set(re.findall(r'(?:src|href)="([^"]+\.js[^"]*)"', html))
    print("js files:", len(js))
    paths = set()
    for path in sorted(js)[:12]:
        url = path if path.startswith("http") else "https://swap.gg" + ("" if path.startswith("/") else "/") + path
        try:
            body = requests.get(url, headers=UA, timeout=40).text
        except Exception:  # noqa: BLE001
            continue
        paths |= set(re.findall(r'["\'](/api/[a-zA-Z0-9/_.-]{2,60})["\']', body))
        paths |= set(re.findall(r'["\'](https://api\.[a-z0-9.-]+[a-zA-Z0-9/_.-]*)["\']', body))
    for p in sorted(paths)[:30]:
        print("  ", p[:110])
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__)

print("\n=== candidate endpoints ===")
for u in (
    "https://api.shadowpay.com/api/prices",
    "https://api.shadowpay.com/api/v1/prices",
    "https://swap.gg/api/prices",
    "https://swap.gg/api/items",
):
    try:
        r = requests.get(u, headers=UA, timeout=25)
        print(f"{r.status_code} {u[:70]:<70} {r.text[:80]}")
    except Exception as e:  # noqa: BLE001
        print(f"ERR {u[:70]} {type(e).__name__}")
