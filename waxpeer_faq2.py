import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

for path in ("/faq/how-to-sell", "/faq/instant-sell", "/faq/trade", "/faq/trade-lock"):
    url = "https://faq.waxpeer.com" + path
    try:
        r = requests.get(url, headers=UA, timeout=25)
        text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S | re.I)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        print(f"=== {path} ({len(text)} chars)")
        for kw in ("online", "token", "Steam", "link", "sign"):
            i = text.lower().find(kw.lower())
            if i >= 0:
                print(f"  [{kw}] ...{text[max(0, i-80):i+220]}...")
    except Exception as e:  # noqa: BLE001
        print(f"=== {path} ERR {type(e).__name__}")
