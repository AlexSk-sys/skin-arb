import json

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}


def probe(name, url, params=None, peek=450):
    try:
        r = requests.get(url, params=params, headers=UA, timeout=45)
        print(f"=== {name} status={r.status_code} bytes={len(r.content)} type={r.headers.get('content-type','')[:30]}")
        if r.status_code != 200:
            print("   ", r.text[:150].replace("\n", " "))
            return None
        try:
            d = r.json()
        except Exception:
            print("    not json:", r.text[:120].replace("\n", " "))
            return None
        if isinstance(d, list):
            print("    list len", len(d), "|", json.dumps(d[0], ensure_ascii=False)[:peek])
        elif isinstance(d, dict):
            print("    keys", list(d.keys())[:12])
            for k in list(d.keys())[:2]:
                print(f"    {k}:", json.dumps(d[k], ensure_ascii=False)[:peek])
        return d
    except Exception as e:  # noqa: BLE001
        print(f"=== {name} ERROR {type(e).__name__}: {str(e)[:120]}")
        return None


probe("lis_skins", "https://lis-skins.com/market_export_json/api_csgo_full.json")
probe("lis_skins_ru", "https://lis-skins.ru/market_export_json/api_csgo_full.json")
probe("csdeals", "https://cs.deals/api/v1/items", {"limit": 5})
probe("mannco", "https://mannco.store/api/items", {"game": "csgo", "limit": 5})
probe("shadowpay", "https://api.shadowpay.com/api/v1/items", {"game": "csgo", "limit": 5})
probe("tradeit", "https://api.tradeit.gg/api/v1/items", {"appId": 730, "limit": 5})
probe("skinsmonkey", "https://api.skinsmonkey.com/api/v1/items", {"limit": 5})
probe("whitemarket", "https://api.whitemarket.gg/api/items", {"limit": 5})
probe(
    "steam_render",
    "https://steamcommunity.com/market/search/render/",
    {"query": "", "start": 0, "count": 5, "search_descriptions": 0,
     "sort_column": "price", "sort_dir": "asc", "appid": 730, "norender": 1},
)
