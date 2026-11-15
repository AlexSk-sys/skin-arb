import re

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
URL = "https://lis-skins.stoplight.io/docs/lis-skins/dzq78x3edc19r-api-overview"

r = requests.get(URL, headers=UA, timeout=30)
html = r.text
print("status", r.status_code, "bytes", len(html))

text = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
text = re.sub(r"<[^>]+>", " ", text)
text = re.sub(r"\s+", " ", text)

for kw in ("Authorization", "Bearer", "api key", "API key", "token", "profile", "settings"):
    i = text.lower().find(kw.lower())
    if i >= 0:
        print(f"[{kw}] ...{text[max(0, i - 120): i + 260]}...")

print("\n--- doc links ---")
links = set(re.findall(r'href="(/docs/lis-skins[^"]*)"', html))
for link in sorted(links)[:25]:
    print(" ", link)
