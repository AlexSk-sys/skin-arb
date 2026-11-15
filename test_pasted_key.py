import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}

FULL = (
    "7a1d6f5ddf97b9411790d1f46d3a7871668530c2832897163d9e8c1b748bbd5c"
    "5260eb11623baf404b61a842abfe02b94a2584e77ed705252f52522b3abbc577"
)
FIRST = FULL[:64]
SECOND = FULL[64:]

for label, key in (("full-128", FULL), ("first-64", FIRST), ("second-64", SECOND)):
    try:
        r = requests.get(
            "https://api.steamanalyst.com/v1/prices",
            params={"market_name": "AK-47 | Redline (Field-Tested)"},
            headers={**UA, "Authorization": f"Bearer {key}"},
            timeout=25,
        )
        print(f"steamanalyst {label}: {r.status_code} {r.text[:120]}")
    except Exception as e:  # noqa: BLE001
        print(f"steamanalyst {label}: ERR {type(e).__name__}")
