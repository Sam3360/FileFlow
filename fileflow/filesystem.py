from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator

from fileflow.models import FileEntry


def list_directory(path: str | Path, include_hidden: bool = False) -> list[FileEntry]:
    target = Path(path)
    if not target.exists() or not target.is_dir():
        return []

    entries: list[FileEntry] = []
    try:
        children = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except OSError:
        return []

    for child in children:
        if child.name.startswith('.') and not include_hidden:
            continue
        try:
            stat = child.stat()
        except OSError:
            continue

        entries.append(
            FileEntry(
                path=child,
                name=child.name,
                is_dir=child.is_dir(),
                size=stat.st_size if child.is_file() else _count_dir_size(child),
                modified=datetime.fromtimestamp(stat.st_mtime),
                hidden=child.name.startswith('.'),
                extension=child.suffix.lower(),
            )
        )
    return entries


def _count_dir_size(path: Path) -> int:
    total = 0
    try:
        for child in path.rglob('*'):
            if child.is_file():
                try:
                    total += child.stat().st_size
                except OSError:
                    continue
    except OSError:
        return 0
    return total


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def create_directory(path: str | Path) -> Path:
    directory = Path(path)
    if directory.exists():
        raise FileExistsError(f"Directory already exists: {directory}")
    directory.mkdir(parents=True, exist_ok=False)
    return directory


def rename_path(path: str | Path, new_name: str) -> Path:
    current = Path(path)
    destination = current.with_name(new_name)
    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")
    current.rename(destination)
    return destination


def copy_item(source: str | Path, destination: str | Path, *, overwrite: bool = False) -> Path:
    source_path = Path(source)
    destination_path = Path(destination)
    if not source_path.exists():
        raise FileNotFoundError(f"Source does not exist: {source_path}")
    if source_path.is_dir():
        if destination_path.exists() and not overwrite:
            raise FileExistsError(f"Destination exists: {destination_path}")
        if destination_path.exists() and overwrite:
            if destination_path.is_dir() and not destination_path.is_symlink():
                shutil.rmtree(destination_path)
            else:
                destination_path.unlink()
        shutil.copytree(source_path, destination_path, dirs_exist_ok=overwrite)
        return destination_path
    if destination_path.exists() and not overwrite:
        raise FileExistsError(f"Destination exists: {destination_path}")
    if destination_path.exists() and overwrite:
        destination_path.unlink()
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination_path)
    return destination_path


def move_item(source: str | Path, destination: str | Path, *, overwrite: bool = False) -> Path:
    source_path = Path(source)
    destination_path = Path(destination)
    if not source_path.exists():
        raise FileNotFoundError(f"Source does not exist: {source_path}")
    if destination_path.exists() and not overwrite:
        raise FileExistsError(f"Destination exists: {destination_path}")
    if destination_path.exists() and overwrite:
        if destination_path.is_dir() and not destination_path.is_symlink():
            shutil.rmtree(destination_path)
        else:
            destination_path.unlink()
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.replace(destination_path)
    return destination_path


def delete_path(path: str | Path) -> None:
    target = Path(path)
    if not target.exists():
        return
    if target.is_dir() and not target.is_symlink():
        shutil.rmtree(target)
    else:
        target.unlink(missing_ok=True)


def search_files(root: str | Path, query: str, recursive: bool = False) -> list[tuple[Path, str]]:
    root_path = Path(root)
    query_lower = query.strip().lower()
    if not query_lower:
        return []

    matches: list[tuple[Path, str]] = []
    iterator: Iterable[Path]
    if recursive:
        iterator = root_path.rglob('*')
    else:
        iterator = root_path.iterdir()

    for item in iterator:
        try:
            if query_lower in item.name.lower():
                matches.append((item, str(item)))
        except OSError:
            continue
    return sorted(matches, key=lambda pair: pair[0].name.lower())
