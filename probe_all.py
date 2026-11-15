import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
}

SITES = [
    ("Skinport", "https://api.skinport.com/v1/items?app_id=730&currency=USD"),
    ("Waxpeer", "https://api.waxpeer.com/v1/prices?game=csgo"),
    ("Market.CSGO", "https://market.csgo.com/api/v2/prices/USD.json"),
    ("DMarket", "https://api.dmarket.com/marketplace-api/v2/offers?gameId=a8db&limit=1"),
    ("CSFloat", "https://csfloat.com/api/v1/listings?limit=1"),
    ("Skinbaron", "https://skinbaron.de/"),
    ("BitSkins", "https://api.bitskins.com/market/insell"),
    ("ShadowPay", "https://api.shadowpay.com/api/prices"),
    ("Mannco.store", "https://mannco.store/"),
    ("CS.Deals", "https://cs.deals/"),
    ("Tradeit.gg", "https://tradeit.gg/"),
    ("SkinsMonkey", "https://skinsmonkey.com/"),
    ("White.Market", "https://white.market/"),
    ("Vault.gg", "https://vault.gg/"),
    ("SkinsBack", "https://skinsback.com/"),
    ("Pricempire", "https://api.pricempire.com/v3/getAllItems"),
    ("CSGOSkins.gg", "https://csgoskins.gg/"),
    ("LIS-SKINS", "https://lis-skins.ru/"),
    ("CS.MONEY", "https://cs.money/"),
    ("TM Market", "https://tm.market/"),
    ("SkinCash", "https://skincash.com/"),
    ("Skin.land", "https://skin.land/"),
    ("CSGO-Skins", "https://csgo-skins.com/"),
    ("Loot.farm", "https://loot.farm/"),
    ("Swap.gg", "https://swap.gg/"),
    ("Buff163", "https://buff.163.com/"),
    ("IGXE", "https://www.igxe.cn/"),
    ("C5Game", "https://www.c5game.com/"),
    ("Youpin898", "https://www.youpin898.com/"),
    ("HaloSkins", "https://www.haloskins.com/"),
    ("ECOSteam", "https://www.ecosteam.cn/"),
    ("ZBT", "https://www.zbt.com/"),
]

print(f"{'site':<16} {'code':>5} {'type':<12} {'size':>8}  note")
print("-" * 90)
for name, url in SITES:
    try:
        r = requests.get(url, headers=UA, timeout=18, allow_redirects=True)
        ct = r.headers.get("content-type", "").split(";")[0][:12]
        note = ""
        if "json" in ct:
            note = "JSON: " + r.text[:80].replace("\n", " ")
        else:
            m = re.search(r"<title[^>]*>(.*?)</title>", r.text, re.S | re.I)
            note = "HTML: " + (m.group(1).strip()[:60] if m else r.text[:60].replace("\n", " "))
        print(f"{name:<16} {r.status_code:>5} {ct:<12} {len(r.content):>8}  {note}")
    except Exception as e:  # noqa: BLE001
        print(f"{name:<16} {'ERR':>5} {'':<12} {'':>8}  {type(e).__name__}: {str(e)[:60]}")
