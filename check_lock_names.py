import ijson
import requests

URL = "https://lis-skins.com/market_export_json/api_csgo_full.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
TARGETS = {
    "Sticker | ropz (Gold) | Austin 2025",
    "UMP-45 | Houndstooth (Factory New)",
}

found: dict[str, list] = {t: [] for t in TARGETS}
with requests.get(URL, stream=True, timeout=600, headers=UA) as r:
    r.raw.decode_content = True
    for item in ijson.items(r.raw, "items.item"):
        name = item.get("name")
        if name in TARGETS and len(found[name]) < 5:
            found[name].append(
                {
                    "id": item.get("id"),
                    "price": item.get("price"),
                    "unlock_at": item.get("unlock_at"),
                }
            )

for name, rows in found.items():
    print("===", name)
    if not rows:
        print("  нет в экспорте")
        continue
    for row in sorted(rows, key=lambda x: x["price"]):
        status = "СВОБОДЕН" if not row["unlock_at"] else f"ЗАБЛОКИРОВАН до {row['unlock_at']}"
        print(f"  ${row['price']:.2f} | id {row['id']} | {status}")
