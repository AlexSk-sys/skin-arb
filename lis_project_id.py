import re

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
html = requests.get(
    "https://lis-skins.stoplight.io/docs/lis-skins/dzq78x3edc19r-api-overview",
    headers=UA,
    timeout=30,
).text

i = html.find('\\"slug\\":\\"lis-skins\\"')
print("slug idx", i)
print(html[max(0, i - 600): i + 80])
print("\nprojectId matches:", set(re.findall(r'projectId\\?":\\?"?([A-Za-z0-9]+)', html))[:5])
print("id near slug:", re.findall(r'\\"id\\":\\"([0-9]+)\\"', html[max(0, i - 600): i]))
