import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

r = requests.get("https://faq.waxpeer.com", headers=UA, timeout=30, allow_redirects=True)
print("status", r.status_code, "->", r.url)
print("bytes", len(r.content))

links = set(re.findall(r'href="([^"]+)"', r.text))
for link in sorted(links):
    low = link.lower()
    if any(k in low for k in ("online", "steam", "token", "sell", "trade", "api")):
        print("  ", link[:120])

text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S | re.I)
text = re.sub(r"<[^>]+>", " ", text)
text = re.sub(r"\s+", " ", text)
for kw in ("Go online", "online", "access token", "Steam token", "Sell items"):
    i = text.lower().find(kw.lower())
    if i >= 0:
        print(f"[{kw}] ...{text[max(0, i-100):i+250]}...")
