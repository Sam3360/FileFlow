from __future__ import annotations

from pathlib import Path

from fileflow.filesystem import copy_item, delete_path, move_item


def format_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    unit_index = 0
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"
    return f"{value:.1f} {units[unit_index]}"


def next_available_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 1
    while True:
        new_candidate = candidate.with_name(f"{stem} ({counter}){suffix}")
        if not new_candidate.exists():
            return new_candidate
        counter += 1


def copy_with_conflict(source: str | Path, destination: str | Path, *, overwrite: bool = False) -> Path:
    source_path = Path(source)
    destination_path = Path(destination)
    if not overwrite and destination_path.exists():
        destination_path = next_available_path(destination_path)
    return copy_item(source_path, destination_path, overwrite=overwrite)


def move_with_conflict(source: str | Path, destination: str | Path, *, overwrite: bool = False) -> Path:
    source_path = Path(source)
    destination_path = Path(destination)
    if not overwrite and destination_path.exists():
        destination_path = next_available_path(destination_path)
    return move_item(source_path, destination_path, overwrite=overwrite)


def delete_selected(paths: list[str | Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        try:
            delete_path(path)
        except OSError as exc:
            errors.append(f"{Path(path)}: {exc}")
    return errors
