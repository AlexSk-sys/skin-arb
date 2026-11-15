import json

import requests
import yaml

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0"}
spec = yaml.safe_load(
    requests.get("https://api.shadowpay.com/doc/openapi_salt_v2.yaml", headers=UA, timeout=40).text
)

# Projects enum may be inline or referenced.
raw = requests.get("https://api.shadowpay.com/doc/openapi_salt_v2.yaml", headers=UA, timeout=40).text
i = raw.find("Projects:")
print("Projects block:", raw[i:i+300].replace("\n", " ") if i >= 0 else "not found")

for path in ("/user/items/prices", "/user/items", "/user/items/buy", "/user/offers", "/user/trade"):
    item = spec.get("paths", {}).get(path)
    if not isinstance(item, dict):
        continue
    print(f"\n=== {path}")
    for method, op in item.items():
        if not isinstance(op, dict):
            continue
        print(f"  {method.upper()}: {op.get('summary')}")
        for p in op.get("parameters", []) or []:
            print(f"    param {p.get('name')} in={p.get('in')} schema={p.get('schema')}")
        rb = op.get("requestBody")
        if isinstance(rb, dict):
            for ctype, body in (rb.get("content") or {}).items():
                print(f"    body {ctype}: {json.dumps(body.get('schema'), ensure_ascii=False)[:500]}")

print("\n=== unauth probe ===")
for url in (
    "https://api.shadowpay.com/api/v2/user/items/prices?project=dota2",
    "https://api.shadowpay.com/api/v2/user/items?project=dota2",
):
    try:
        r = requests.get(url, headers=UA, timeout=25)
        print(r.status_code, url[:70], r.text[:150])
    except Exception as e:  # noqa: BLE001
        print("ERR", url[:70], type(e).__name__)
