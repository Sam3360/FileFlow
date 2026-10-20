from __future__ import annotations

from pathlib import Path
from typing import Iterator


def iter_name_matches(root: str | Path, query: str, recursive: bool = False) -> Iterator[Path]:
    root_path = Path(root)
    query_text = query.strip().lower()
    if not query_text:
        return iter(())

    if recursive:
        iterator = root_path.rglob('*')
    else:
        iterator = root_path.iterdir()

    for item in iterator:
        try:
            if item.name.lower().find(query_text) >= 0:
                yield item
        except OSError:
            continue
