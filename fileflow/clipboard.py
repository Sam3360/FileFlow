from __future__ import annotations

import subprocess
from pathlib import Path

from fileflow.models import ClipboardState


def set_system_clipboard_text(text: str) -> None:
    if not text:
        return
    subprocess.run(["powershell", "-NoProfile", "-Command", "Set-Clipboard", "-Value", text], check=False)


def copy_full_path_to_clipboard(path: str | Path) -> None:
    set_system_clipboard_text(str(Path(path)))


def build_clipboard_state(paths: list[str | Path], mode: str) -> ClipboardState:
    return ClipboardState(mode=mode, paths=[str(Path(item)) for item in paths])
