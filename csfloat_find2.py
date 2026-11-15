import re
from urllib.parse import quote, unquote

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

for host in (
    "https://api.csfloat.com/",
    "https://docs.csfloat.dev/",
    "https://csfloat.dev/",
    "https://docs.csfloat.com/",
):
    try:
        r = requests.get(host, headers=UA, timeout=15, allow_redirects=True)
        m = re.search(r"<title[^>]*>(.*?)</title>", r.text, re.S | re.I)
        title = m.group(1).strip()[:60] if m else ""
        print(r.status_code, "->", r.url[:80], "| title:", title)
    except Exception as e:  # noqa: BLE001
        print("ERR", host, type(e).__name__)

print("\n=== Bing ===")
try:
    r = requests.get(
        "https://www.bing.com/search?q=" + quote("csfloat api documentation"),
        headers=UA,
        timeout=30,
    )
    print("status", r.status_code, "len", len(r.text))
    links = re.findall(r'<a[^>]+href="(https?://[^"]+)"', r.text)
    shown = 0
    for u in links:
        if "csfloat" in u.lower() and "bing.com" not in u:
            print("   ", unquote(u)[:120])
            shown += 1
            if shown >= 12:
                break
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__, str(e)[:80])
