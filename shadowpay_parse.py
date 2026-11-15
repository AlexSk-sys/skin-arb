import json

import requests

try:
    import yaml
except ImportError:
    print("PyYAML missing")
    raise SystemExit(1)

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0"}
r = requests.get(
    "https://api.shadowpay.com/doc/openapi_salt_v2.yaml", headers=UA, timeout=40
)
spec = yaml.safe_load(r.text)

print("servers:", spec.get("servers"))
print("securitySchemes:", json.dumps(spec.get("components", {}).get("securitySchemes", {}), ensure_ascii=False)[:300])

for path in (
    "/user/items/prices",
    "/user/items",
    "/user/items/buy",
    "/user/offers",
    "/user/trade",
    "/user/token",
):
    item = spec.get("paths", {}).get(path)
    if not item:
        continue
    print(f"\n=== {path}")
    for method, op in item.items():
        print(f"  {method.upper()}: {op.get('summary')}")
        params = op.get("parameters", [])
        for p in params:
            print(f"    param {p.get('name')} in={p.get('in')} required={p.get('required')} schema={p.get('schema')}")
        rb = op.get("requestBody")
        if rb:
            content = rb.get("content", {})
            for ctype, body in content.items():
                print(f"    body {ctype}: {json.dumps(body.get('schema'), ensure_ascii=False)[:400]}")
