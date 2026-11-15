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
    ("market", "Steam Market", "https://steamcommunity.com/market/"),
    ("market", "Skinport", "https://skinport.com/"),
    ("market", "CSFloat", "https://csfloat.com/"),
    ("market", "Waxpeer", "https://waxpeer.com/"),
    ("market", "Market.CSGO", "https://market.csgo.com/"),
    ("market", "DMarket", "https://dmarket.com/"),
    ("market", "Skinbaron", "https://skinbaron.de/"),
    ("market", "BitSkins", "https://bitskins.com/"),
    ("market", "ShadowPay", "https://shadowpay.com/"),
    ("market", "Mannco.store", "https://mannco.store/"),
    ("market", "CS.Deals", "https://cs.deals/"),
    ("market", "Tradeit.gg", "https://tradeit.gg/"),
    ("market", "SkinsMonkey", "https://skinsmonkey.com/"),
    ("market", "White.Market", "https://white.market/"),
    ("market", "Vault.gg", "https://vault.gg/"),
    ("market", "SkinsBack", "https://skinsback.com/"),
    ("market", "Lootbear", "https://lootbear.com/"),
    ("market", "Skinwallet", "https://skinwallet.com/"),
    ("market", "CSGOFast", "https://csgofast.com/"),
    ("market", "SkinsCash", "https://skincash.com/"),
    ("market", "Swap.gg", "https://swap.gg/"),
    ("market", "Loot.farm", "https://loot.farm/"),
    ("market", "CS.MONEY", "https://cs.money/"),
    ("market", "TM Market", "https://tm.market/"),
    ("market", "Skin.land", "https://skin.land/"),
    ("market", "CSGO-Skins", "https://csgo-skins.com/"),
    ("market", "LIS-SKINS", "https://lis-skins.com/"),
    ("market", "SkinsFarm", "https://skinsfarm.com/"),
    ("market", "ITrade.gg", "https://itrade.gg/"),
    ("market", "SkinShark", "https://skinshark.com/"),
    ("market", "LokiSkins", "https://lokiskins.com/"),
    ("market", "Buff Market", "https://buff.market/"),
    ("market", "CS2Exchange", "https://cs2exchange.com/"),
    ("market", "SkinArena", "https://skinarena.com/"),
    ("market", "SkinDeals", "https://skindeals.com/"),
    ("market", "TradeSkins", "https://tradeskins.com/"),
    ("china", "Buff163", "https://buff.163.com/"),
    ("china", "IGXE", "https://www.igxe.cn/"),
    ("china", "C5Game", "https://www.c5game.com/"),
    ("china", "Youpin898", "https://www.youpin898.com/"),
    ("china", "HaloSkins", "https://www.haloskins.com/"),
    ("china", "ECOSteam", "https://www.ecosteam.cn/"),
    ("china", "ZBT", "https://www.zbt.com/"),
    ("china", "91Skins", "https://www.91skins.com/"),
    ("tracker", "CSGOSkins.gg", "https://csgoskins.gg/"),
    ("tracker", "Pricempire", "https://pricempire.com/"),
    ("tracker", "CSGOStash", "https://csgostash.com/"),
    ("tracker", "SteamAnalyst", "https://csgo.steamanalyst.com/"),
    ("tracker", "CSGOBackpack", "https://csgobackpack.net/"),
    ("tracker", "SkinSearch", "https://skinsearch.com/"),
    ("gambling", "CSGORoll", "https://csgoroll.com/"),
    ("gambling", "CSGOEmpire", "https://csgoempire.com/"),
    ("gambling", "Rollbit", "https://rollbit.com/"),
    ("gambling", "KeyDrop", "https://key-drop.com/"),
    ("gambling", "Hellcase", "https://hellcase.com/"),
    ("gambling", "Daddyskins", "https://daddyskins.com/"),
    ("gambling", "Clash.gg", "https://clash.gg/"),
    ("gambling", "SkinClub", "https://skin.club/"),
]

print(f"{'cat':<9} {'site':<16} {'code':>5} {'type':<11} {'size':>8}  note")
print("-" * 100)
stats = {"ok": 0, "cf": 0, "err": 0}
for cat, name, url in SITES:
    try:
        r = requests.get(url, headers=UA, timeout=15, allow_redirects=True)
        ct = r.headers.get("content-type", "").split(";")[0][:11]
        m = re.search(r"<title[^>]*>(.*?)</title>", r.text, re.S | re.I)
        title = m.group(1).strip()[:55] if m else ""
        if "just a moment" in title.lower() or "attention required" in title.lower():
            note = "CLOUDFLARE challenge"
            stats["cf"] += 1
        elif "json" in ct:
            note = "JSON " + r.text[:60].replace("\n", " ")
            stats["ok"] += 1
        else:
            note = title or r.text[:55].replace("\n", " ")
            stats["ok"] += 1
        print(f"{cat:<9} {name:<16} {r.status_code:>5} {ct:<11} {len(r.content):>8}  {note}")
    except Exception as e:  # noqa: BLE001
        stats["err"] += 1
        print(f"{cat:<9} {name:<16} {'ERR':>5} {'':<11} {'':>8}  {type(e).__name__}: {str(e)[:45]}")

print("-" * 100)
print(f"всего {len(SITES)}: ответили {stats['ok']}, cloudflare {stats['cf']}, недоступны {stats['err']}")
