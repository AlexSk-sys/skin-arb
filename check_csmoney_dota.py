import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

for url in ("https://cs.money/dota2", "https://cs.money/ru/dota2", "https://loot.farm/"):
    try:
        r = requests.get(url, headers=UA, timeout=25, allow_redirects=True)
        text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        t = re.search(r"<title[^>]*>(.*?)</title>", r.text, re.S | re.I)
        title = t.group(1).strip()[:70] if t else ""
        found = [k for k in ("Dota", "USDT", "СБП", "карт", "МИР", "crypto") if k.lower() in text.lower()]
        print(f"{url[:40]:<40} {r.status_code} {title:<50} {found}")
    except Exception as e:  # noqa: BLE001
        print(f"{url[:40]:<40} ERR {type(e).__name__}")
