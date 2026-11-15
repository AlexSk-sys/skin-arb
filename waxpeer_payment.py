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

ENDPOINTS = [
    ("/v1/user", {}),
    ("/v1/payment/currencies/trx", {}),
    ("/v1/payment/currencies", {}),
    ("/v1/payment/deposit", {}),
    ("/v1/deposit", {}),
    ("/v1/withdraw", {}),
    ("/v1/get-deposit-address", {}),
]

for path, extra in ENDPOINTS:
    try:
        r = requests.get(
            "https://api.waxpeer.com" + path,
            params={"api": WX, **extra},
            headers=UA,
            timeout=30,
        )
        print(f"{path:<32} {r.status_code} {r.text[:220].replace(chr(10), ' ')}")
    except Exception as e:  # noqa: BLE001
        print(f"{path:<32} ERR {type(e).__name__}")
