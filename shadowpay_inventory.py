import os
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


SP = key("SHADOWPAY_API_TOKEN")
H = {**UA, "Authorization": f"Bearer {SP}"}
BASE = "https://api.shadowpay.com/api/v2"

for path, params in (
    ("/user/inventory", {"project": "dota2"}),
    ("/user/offers", {}),
):
    try:
        r = requests.get(BASE + path, params=params, headers=H, timeout=40)
        print(f"=== {path} {r.status_code}")
        print(r.text[:600].replace("\n", " "))
    except Exception as e:  # noqa: BLE001
        print(f"=== {path} ERR {type(e).__name__}")
