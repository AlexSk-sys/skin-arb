import json

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}


def probe(name, url, params=None, peek=400):
    try:
        r = requests.get(url, params=params, headers=UA, timeout=45)
        print(f"=== {name} status={r.status_code} bytes={len(r.content)}")
        if r.status_code != 200:
            print("   ", r.text[:140].replace("\n", " "))
            return None
        try:
            d = r.json()
        except Exception:
            print("    not json:", r.text[:110].replace("\n", " "))
            return None
        if isinstance(d, list):
            print("    list len", len(d), "|", json.dumps(d[0], ensure_ascii=False)[:peek])
        elif isinstance(d, dict):
            print("    keys", list(d.keys())[:12])
            for k in list(d.keys())[:2]:
                print(f"    {k}:", json.dumps(d[k], ensure_ascii=False)[:peek])
        return d
    except Exception as e:  # noqa: BLE001
        print(f"=== {name} ERROR {type(e).__name__}: {str(e)[:100]}")
        return None


probe("pricempire", "https://api.pricempire.com/v3/getAllItems", {"sources": "steam"})
probe("csgoskins", "https://api.csgoskins.gg/v1/items", {"limit": 5})
probe("csgotrader_v6_gz", "https://prices.csgotrader.app/latest/prices_v6.json", {"t": 1})
probe("skinbaron_docs", "https://api.skinbaron.de/GetPriceList")
probe(
    "steam_render",
    "https://steamcommunity.com/market/search/render/",
    {"query": "", "start": 0, "count": 5, "search_descriptions": 0,
     "sort_column": "price", "sort_dir": "asc", "appid": 730, "norender": 1},
)
