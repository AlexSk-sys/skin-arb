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
data, _ = json.JSONDecoder().raw_decode(html[m.end() :])

inner = json.loads(data["2351030891"]["data"])
nodes = inner["defaultBranchNodes"]
print("nodes:", len(nodes))

for node in nodes[:8]:
    snap = node.get("snapshot") or {}
    print(f"\n=== {node.get('name')} | snapshot keys: {list(snap.keys())}")
    for k, v in snap.items():
        if isinstance(v, str) and v:
            print(f"  {k}: {v[:220]}")
        elif isinstance(v, (int, float, bool)):
            print(f"  {k}: {v}")
