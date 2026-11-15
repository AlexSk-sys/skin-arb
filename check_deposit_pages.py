import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

URLS = [
    ("waxpeer deposit", "https://waxpeer.com/deposit"),
    ("waxpeer en deposit", "https://waxpeer.com/en/deposit"),
    ("waxpeer wallet", "https://waxpeer.com/profile/wallet"),
    ("mcs deposit", "https://market.csgo.com/en/deposit"),
    ("mcs profile deposit", "https://market.csgo.com/en/profile/deposit"),
    ("mcs topup", "https://market.csgo.com/en/topup"),
    ("white deposit", "https://white.market/deposit"),
    ("csmoney deposit", "https://cs.money/deposit"),
    ("shadowpay deposit", "https://shadowpay.com/deposit"),
]

PAY = ["СБП", "SBP", "МИР", "Mir", "Visa", "Mastercard", "карт", "card", "USDT", "crypto", "bank", "Payeer", "ЮMoney", "YooMoney", "QIWI"]

for name, url in URLS:
    try:
        r = requests.get(url, headers=UA, timeout=20, allow_redirects=True)
        text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        found = [k for k in PAY if k.lower() in text.lower()]
        print(f"{name:<22} {r.status_code} -> {r.url[:60]:<60} {', '.join(found) if found else '—'}")
    except Exception as e:  # noqa: BLE001
        print(f"{name:<22} ERR {type(e).__name__}")
