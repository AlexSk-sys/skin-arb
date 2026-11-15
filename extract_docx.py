import re
import zipfile
from pathlib import Path

PATH = Path(r"C:\Users\AgentPC\Desktop\апи кс2.docx")


def mask(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}…{value[-4:]} (len {len(value)})"


def looks_secret(token: str) -> bool:
    if len(token) < 24:
        return False
    has_digit = any(c.isdigit() for c in token)
    has_alpha = any(c.isalpha() for c in token)
    return has_digit and has_alpha


with zipfile.ZipFile(PATH) as z:
    xml = z.read("word/document.xml").decode("utf-8", "ignore")

paragraphs = re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)
lines: list[str] = []
for p in paragraphs:
    text = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S))
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    if text.strip():
        lines.append(text.strip())

print(f"paragraphs: {len(lines)}\n")
for line in lines:
    redacted = re.sub(
        r"[A-Za-z0-9_\-]{20,}", lambda m: mask(m.group(0)) if looks_secret(m.group(0)) else m.group(0), line
    )
    print(redacted)
