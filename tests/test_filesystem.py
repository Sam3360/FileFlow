from __future__ import annotations

from pathlib import Path

import pytest

from fileflow.filesystem import (
    copy_item,
    create_directory,
    delete_path,
    list_directory,
    move_item,
    rename_path,
    search_files,
)


@pytest.fixture
def tmp_tree(tmp_path: Path):
    (tmp_path / "alpha").mkdir()
    (tmp_path / "alpha" / "inner.txt").write_text("hello\n", encoding="utf-8")
    (tmp_path / "beta.txt").write_text("world\n", encoding="utf-8")
    hidden = tmp_path / ".hidden"
    hidden.mkdir()
    return tmp_path


def test_list_directory_and_sorting(tmp_tree: Path):
    entries = list_directory(tmp_tree)
    names = [entry.name for entry in entries]
    assert "alpha" in names
    assert "beta.txt" in names
    assert ".hidden" not in names

    hidden_entries = list_directory(tmp_tree, include_hidden=True)
    assert ".hidden" in [entry.name for entry in hidden_entries]


def test_create_rename_and_delete(tmp_tree: Path):
    new_dir = tmp_tree / "gamma"
    create_directory(new_dir)
    target = rename_path(new_dir, "delta")
    assert target == tmp_tree / "delta"
    delete_path(target)
    assert not target.exists()


def test_copy_and_move_items(tmp_tree: Path):
    source = tmp_tree / "beta.txt"
    destination = tmp_tree / "copy_target.txt"
    copied = copy_item(source, destination)
    assert copied.exists()
    assert copied.read_text(encoding="utf-8") == "world\n"

    moved = tmp_tree / "moved.txt"
    move_item(destination, moved)
    assert not destination.exists()
    assert moved.read_text(encoding="utf-8") == "world\n"


def test_copy_dir_with_conflict_and_move_dir(tmp_tree: Path):
    root = tmp_tree / "alpha"
    copy_dest = tmp_tree / "alpha_copy"
    copy_item(root, copy_dest)
    assert (copy_dest / "inner.txt").exists()

    move_dest = tmp_tree / "alpha_moved"
    move_item(copy_dest, move_dest)
    assert move_dest.exists()
    assert not copy_dest.exists()


def test_search_files(tmp_tree: Path):
    assert [item.name for item in [p for p, _ in search_files(tmp_tree, "beta")]] == ["beta.txt"]
    assert any("inner.txt" in item.name for item in [p for p, _ in search_files(tmp_tree, "inner", recursive=True)])


def test_inaccessible_directory_handling(tmp_path: Path):
    unreadable = tmp_path / "locked"
    unreadable.mkdir()
    unreadable.chmod(0o000)
    try:
        assert list_directory(unreadable) == []
    finally:
        unreadable.chmod(0o700)


def test_destination_conflict_raises(tmp_tree: Path):
    source = tmp_tree / "beta.txt"
    target = tmp_tree / "beta.txt"
    with pytest.raises(FileExistsError):
        copy_item(source, target)


def test_unicode_and_spaces_filenames(tmp_path: Path):
    path = tmp_path / "résumé file.txt"
    path.write_text("ok", encoding="utf-8")
    entries = list_directory(tmp_path)
    assert "résumé file.txt" in [entry.name for entry in entries]
