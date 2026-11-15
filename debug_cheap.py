import json
import os
import winreg

import requests

import scan3  # type: ignore

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}


def get_key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = get_key("WAXPEER_API_KEY")
MC = get_key("MARKET_CSGO_API_KEY")

wax = scan3.fetch_waxpeer()
mcs = scan3.fetch_market_csgo()
rows = scan3.evaluate(scan3.build_table(wax, mcs, {}))
cheap = [
    r for r in rows
    if r["buy"] <= 5 and r["margin"] >= 0.10 and r["margin"] <= 0.60
    and r["vol_buy"] >= 20 and r["vol_sell"] >= 20
]
cheap.sort(key=lambda r: r["profit"], reverse=True)

for r in cheap[:8]:
    name = r["item"]
    print("===", name, f"wax ${r['buy']:.2f}")
    for path in ("/v2/search-items-by-name", "/v1/search-items-by-name"):
        for pname in ("name", "search"):
            try:
                resp = requests.get(
                    "https://api.waxpeer.com" + path,
                    params={"api": WX, pname: name},
                    headers=UA,
                    timeout=30,
                )
                body = resp.text[:160].replace("\n", " ")
                print(f"  wax {path}?{pname} -> {resp.status_code} {body}")
            except Exception as e:  # noqa: BLE001
                print(f"  wax {path} ERR {type(e).__name__}")
    try:
        resp = requests.get(
            "https://market.csgo.com/api/v2/search-item-by-hash-name",
            params={"key": MC, "hash_name": name, "currency": "USD"},
            headers=UA,
            timeout=30,
        )
        data = resp.json().get("data") or []
        print(f"  mcs -> {resp.status_code} items={len(data)}")
    except Exception as e:  # noqa: BLE001
        print(f"  mcs ERR {type(e).__name__}")
