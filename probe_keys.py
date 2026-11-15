import json
import os
import winreg

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def get_key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


def show(name, r, peek=500):
    print(f"=== {name} status={r.status_code} bytes={len(r.content)}")
    try:
        d = r.json()
    except Exception:
        print("   ", r.text[:200].replace("\n", " "))
        return
    if isinstance(d, dict):
        print("    keys:", list(d.keys())[:12])
        print("    ", json.dumps(d, ensure_ascii=False)[:peek])
    elif isinstance(d, list):
        print("    list len", len(d), "|", json.dumps(d[0], ensure_ascii=False)[:peek])


pk = get_key("PRICEMPIRE_API_KEY")
ck = get_key("CSFLOAT_API_KEY")
dp = get_key("DMARKET_PUBLIC_KEY")

# Pricempire: query-param auth
try:
    r = requests.get(
        "https://api.pricempire.com/v3/getAllItems",
        params={"api_key": pk, "sources": "steam", "currency": "USD"},
        headers=UA,
        timeout=60,
    )
    show("pricempire query-param", r)
except Exception as e:  # noqa: BLE001
    print("pricempire query-param ERR", type(e).__name__, str(e)[:100])

# Pricempire: bearer auth
try:
    r = requests.get(
        "https://api.pricempire.com/v3/getAllItems",
        params={"sources": "steam", "currency": "USD"},
        headers={**UA, "Authorization": f"Bearer {pk}"},
        timeout=60,
    )
    show("pricempire bearer", r)
except Exception as e:  # noqa: BLE001
    print("pricempire bearer ERR", type(e).__name__, str(e)[:100])

# CSFloat
try:
    r = requests.get(
        "https://csfloat.com/api/v1/me", headers={**UA, "Authorization": ck}, timeout=40
    )
    show("csfloat /me", r)
except Exception as e:  # noqa: BLE001
    print("csfloat ERR", type(e).__name__, str(e)[:100])

# DMarket
try:
    r = requests.get(
        "https://api.dmarket.com/account/v1/balance",
        headers={**UA, "X-Api-Key": dp},
        timeout=40,
    )
    show("dmarket balance", r)
except Exception as e:  # noqa: BLE001
    print("dmarket ERR", type(e).__name__, str(e)[:100])
