import json

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/0.1"}


def probe(name, url, params=None, peek=600):
    try:
        r = requests.get(url, params=params, headers=UA, timeout=60)
        print(f"=== {name} status={r.status_code} bytes={len(r.content)}")
        if r.status_code != 200:
            print(r.text[:200])
            return None
        try:
            d = r.json()
        except Exception:
            print("not json:", r.text[:150])
            return None
        if isinstance(d, list):
            print("list len", len(d), "| sample:", json.dumps(d[0], ensure_ascii=False)[:peek])
        elif isinstance(d, dict):
            print("keys", list(d.keys())[:15])
            for k in list(d.keys())[:3]:
                v = d[k]
                print(f"-- {k}:", json.dumps(v, ensure_ascii=False)[:peek])
        return d
    except Exception as e:  # noqa: BLE001
        print(f"=== {name} ERROR {type(e).__name__}: {e}")
        return None


probe("market_csgo", "https://market.csgo.com/api/v2/prices/USD.json")
probe("csgobackpack", "https://csgobackpack.net/api/GetItemsList/v2/")
probe("skinbaron_public", "https://api.skinbaron.de/Account/GetBalance")
probe("csdeals", "https://cs.deals/api/v1/stats")
probe("swapgg", "https://api.swap.gg/v1/prices")
