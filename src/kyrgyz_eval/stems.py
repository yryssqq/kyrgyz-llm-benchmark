from __future__ import annotations

from pathlib import Path


def read_stems(path: str | Path) -> list[tuple[str, str | None]]:
    stems: list[tuple[str, str | None]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        if "|" in line:
            stem, irregular = line.split("|", 1)
            stems.append((stem.strip(), irregular.strip() or None))
        else:
            stems.append((line, None))
    return stems
