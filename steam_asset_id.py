import json

import requests

STEAM_ID = "76561198848755367"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}

for app_id, label in ((570, "Dota 2"), (730, "CS2")):
    try:
        r = requests.get(
            f"https://steamcommunity.com/inventory/{STEAM_ID}/{app_id}/2",
            params={"l": "english", "count": 500},
            headers=UA,
            timeout=40,
        )
        print(f"{label}: {r.status_code} bytes {len(r.content)}")
        if r.status_code != 200:
            continue
        d = r.json()
        if not d or not d.get("success"):
            print("  ", json.dumps(d, ensure_ascii=False)[:200] if d else r.text[:200])
            continue
        assets = d.get("assets", [])
        descs = {x["classid"]: x for x in d.get("descriptions", [])}
        print("  items:", len(assets))
        for a in assets:
            desc = descs.get(a.get("classid"), {})
            name = desc.get("market_hash_name") or desc.get("name")
            if name and "Mortar Forge" in name:
                print("  FOUND asset_id:", a.get("assetid"), "| classid:", a.get("classid"), "|", name)
    except Exception as e:  # noqa: BLE001
        print(f"{label} ERR {type(e).__name__}: {str(e)[:80]}")
