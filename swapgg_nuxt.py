import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
html = requests.get("https://swap.gg/dota2/trade", headers=UA, timeout=30).text
print("bytes", len(html))
for marker in ("__NUXT_DATA__", "__NUXT__", "window.__", "api"):
    i = html.find(marker)
    print(f"[{marker}] idx={i}")
    if i >= 0:
        print("  ", html[max(0, i - 100): i + 300].replace("\n", " ")[:400])

print("\nscript srcs:")
for s in sorted(set(re.findall(r'src="([^"]+\.js[^"]*)"', html)))[:15]:
    print("  ", s[:120])
