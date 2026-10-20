from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal


@dataclass(slots=True)
class FileEntry:
    path: Path
    name: str
    is_dir: bool
    size: int
    modified: datetime
    hidden: bool
    extension: str


ClipboardMode = Literal["copy", "move"]


@dataclass(slots=True)
class ClipboardState:
    mode: ClipboardMode | None = None
    paths: list[str] = field(default_factory=list)

    @property
    def has_items(self) -> bool:
        return bool(self.paths)
