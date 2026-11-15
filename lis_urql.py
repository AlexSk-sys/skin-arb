import json
import re

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
html = requests.get(
    "https://lis-skins.stoplight.io/docs/lis-skins/dzq78x3edc19r-api-overview",
    headers=UA,
    timeout=30,
).text

m = re.search(r"window\.URQL_DATA\s*=\s*", html)
if not m:
    print("URQL_DATA not found")
    raise SystemExit(1)

try:
    data, _end = json.JSONDecoder().raw_decode(html[m.end() :])
except json.JSONDecodeError as exc:
    print("json error", exc)
    raise SystemExit(1)

print("top keys:", list(data.keys()))


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, obj


for key, value in data.items():
    if not (isinstance(value, dict) and isinstance(value.get("data"), str)):
        continue
    try:
        inner = json.loads(value["data"])
    except json.JSONDecodeError:
        continue
    print(f"\n[{key}] inner keys: {list(inner.keys())[:10] if isinstance(inner, dict) else type(inner)}")
    hits = 0
    for path, leaf in walk(inner):
        if isinstance(leaf, str) and any(k in leaf.lower() for k in ("buy", "item_id", "authorization", "bearer")):
            print(f"  {path}: {leaf[:300]}")
            hits += 1
            if hits >= 12:
                break
    if hits == 0:
        print("  no buy/auth strings; sample:")
        for path, leaf in list(walk(inner))[:15]:
            print(f"  {path}: {str(leaf)[:160]}")
