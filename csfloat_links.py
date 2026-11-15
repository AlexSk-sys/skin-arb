import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

CANDIDATES = [
    "https://csfloat.com/profile",
    "https://csfloat.com/api",
    "https://csfloat.com/api-docs",
    "https://docs.csfloat.com/",
    "https://csfloat.com/docs/api",
    "https://csfloat.com/developer",
]

for url in CANDIDATES:
    try:
        r = requests.get(url, headers=UA, timeout=20, allow_redirects=True)
        print(r.status_code, "->", r.url[:100], "len", len(r.text))
    except Exception as e:  # noqa: BLE001
        print("ERR", url, type(e).__name__, str(e)[:80])

print("--- api links found on /profile ---")
try:
    html = requests.get("https://csfloat.com/profile", headers=UA, timeout=20).text
    found = set(re.findall(r'href="([^"]*api[^"]*)"', html, re.I))
    found |= set(re.findall(r"(https://[a-z0-9./_-]*api[a-z0-9./_-]*)", html, re.I))
    for link in sorted(found)[:25]:
        print(" ", link)
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__, str(e)[:80])
