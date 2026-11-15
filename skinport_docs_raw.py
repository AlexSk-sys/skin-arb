import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
r = requests.get("https://docs.skinport.com/", headers=UA, timeout=25)
html = r.text
print("status", r.status_code, "bytes", len(html))
print("--- hrefs ---")
for link in sorted(set(re.findall(r'href="([^"]+)"', html)))[:50]:
    print("  ", link[:140])
print("--- script srcs ---")
for src in sorted(set(re.findall(r'src="([^"]+)"', html)))[:20]:
    print("  ", src[:140])
print("--- text head ---")
text = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
text = re.sub(r"<[^>]+>", " ", text)
text = re.sub(r"\s+", " ", text)
print(text[:1500])
