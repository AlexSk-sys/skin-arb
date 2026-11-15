import json

import requests
import yaml

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0"}
spec = yaml.safe_load(
    requests.get("https://api.shadowpay.com/doc/openapi_salt_v2.yaml", headers=UA, timeout=40).text
)

for path in ("/user/inventory", "/user/items/steam", "/user/items"):
    item = spec.get("paths", {}).get(path)
    if not isinstance(item, dict):
        continue
    print(f"\n=== {path}")
    for method, op in item.items():
        if not isinstance(op, dict):
            continue
        print(f"  {method.upper()}: {op.get('summary')}")
        for p in op.get("parameters", []) or []:
            print(f"    param {p.get('name')} required={p.get('required')} schema={p.get('schema')}")
        responses = op.get("responses") or {}
        for code, resp in responses.items():
            content = (resp.get("content") or {}) if isinstance(resp, dict) else {}
            for ctype, body in content.items():
                print(f"    {code} {ctype}: {json.dumps(body.get('schema'), ensure_ascii=False)[:400]}")
