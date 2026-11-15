import os
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")
TRADE_URL = key("STEAM_TRADE_URL")

for method, payload in (
    ("POST", {"tradelink": TRADE_URL}),
    ("POST", {"trade_url": TRADE_URL}),
    ("GET", None),
):
    try:
        if method == "POST":
            r = requests.post(
                "https://api.waxpeer.com/v1/check-tradelink",
                params={"api": WX},
                json=payload,
                headers=UA,
                timeout=40,
            )
        else:
            r = requests.get(
                "https://api.waxpeer.com/v1/check-tradelink",
                params={"api": WX, "tradelink": TRADE_URL},
                headers=UA,
                timeout=40,
            )
        print(f"{method} {payload and list(payload)[0]}: {r.status_code} {r.text[:300]}")
    except Exception as e:  # noqa: BLE001
        print(f"{method} ERR {type(e).__name__}")
