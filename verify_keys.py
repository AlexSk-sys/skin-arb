import os
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}


def get_key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


def show(label: str, r: requests.Response, peek: int = 160) -> None:
    body = r.text[:peek].replace("\n", " ")
    print(f"{label:<28} {r.status_code}  {body}")


cf = get_key("CSFLOAT_API_KEY")
wx = get_key("WAXPEER_API_KEY")
mc = get_key("MARKET_CSGO_API_KEY")

show("csfloat /me", requests.get(
    "https://csfloat.com/api/v1/me", headers={**UA, "Authorization": cf}, timeout=30
))

for path in ("/v1/user", "/v1/get-user", "/v1/me"):
    try:
        show(f"waxpeer {path}", requests.get(
            "https://api.waxpeer.com" + path, params={"api": wx}, headers=UA, timeout=30
        ))
    except Exception as e:  # noqa: BLE001
        print(f"waxpeer {path:<20} ERR {type(e).__name__}")

for path in ("/api/v2/get-money", "/api/v2/get-balance"):
    try:
        show(f"mcs {path}", requests.get(
            "https://market.csgo.com" + path, params={"key": mc}, headers=UA, timeout=30
        ))
    except Exception as e:  # noqa: BLE001
        print(f"mcs {path:<24} ERR {type(e).__name__}")
