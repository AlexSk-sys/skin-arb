import requests

r = requests.get(
    "https://lis-skins.com/market_export_json/api_csgo_full.json",
    stream=True,
    timeout=90,
    headers={"User-Agent": "Mozilla/5.0"},
)
print("status", r.status_code, "encoding", r.headers.get("content-encoding"))
raw = r.raw.read(4096, decode_content=True)
print(raw.decode("utf-8", "ignore")[:3000])
r.close()
