import re
from pathlib import Path

PATH = Path(r"C:\Users\AgentPC\Desktop\апи кс2.docx")


def mask(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}…{value[-4:]} (len {len(value)})"


text = PATH.read_text(encoding="utf-8", errors="ignore")
print(f"lines: {len(text.splitlines())}, chars: {len(text)}\n")

for i, line in enumerate(text.splitlines(), 1):
    stripped = line.strip()
    if not stripped:
        print(f"{i:>2}: <empty>")
        continue
    # Mask anything that looks like a credential.
    redacted = re.sub(r"[A-Za-z0-9_\-]{16,}", lambda m: mask(m.group(0)), stripped)
    print(f"{i:>2}: {redacted}")
