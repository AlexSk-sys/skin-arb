import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

for path in ("/faq/how-to-sell", "/faq/instant-sell", "/faq/fees-sell"):
    url = "https://faq.waxpeer.com" + path
    try:
        r = requests.get(url, headers=UA, timeout=25)
        text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        for kw in ("minimum", "minimum price", "min price", "0.03", "0.01", "$0"):
            i = text.lower().find(kw.lower())
            if i >= 0:
                print(f"[{path} | {kw}] ...{text[max(0, i-120):i+200]}...")
    except Exception as e:  # noqa: BLE001
        print(f"{path} ERR {type(e).__name__}")
