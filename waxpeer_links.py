import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

r = requests.get("https://docs.waxpeer.com/authentication", headers=UA, timeout=30)
print("docs status", r.status_code)
links = set(re.findall(r'href="([^"]+)"', r.text))
for link in sorted(links):
    if "waxpeer.com" in link and "docs" not in link:
        print("  ", link[:120])

print("\n=== profile pages ===")
for url in (
    "https://waxpeer.com/profile",
    "https://waxpeer.com/profile/user?tab=security",
    "https://waxpeer.com/profile/user?tab=steam",
    "https://waxpeer.com/sell",
    "https://waxpeer.com/sell-items",
    "https://waxpeer.com/trade",
    "https://waxpeer.com/online",
):
    try:
        resp = requests.get(url, headers=UA, timeout=20, allow_redirects=True)
        m = re.search(r"<title[^>]*>(.*?)</title>", resp.text, re.S | re.I)
        title = m.group(1).strip()[:50] if m else ""
        print(f"{resp.status_code} {url[:55]:<55} -> {resp.url[:55]:<55} {title}")
    except Exception as e:  # noqa: BLE001
        print(f"ERR {url[:55]} {type(e).__name__}")
