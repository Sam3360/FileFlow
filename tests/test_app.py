import asyncio
from pathlib import Path

from textual.widgets import ListView

from fileflow.app import FileFlowApp


def test_app_renders_directory_and_opens_folder(tmp_path: Path):
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "inside.txt").write_text("content", encoding="utf-8")
    (tmp_path / "file.txt").write_text("content", encoding="utf-8")

    app = FileFlowApp()
    app.current_path = str(tmp_path)

    async def exercise_app():
        async with app.run_test() as pilot:
            file_list = app.query_one("#file-list", ListView)
            assert [entry.name for entry in app.entries] == ["folder", "file.txt"]
            assert len(file_list.children) == 2

            file_list.focus()
            await pilot.press("enter")
            await pilot.pause()

            assert app.current_path == str(folder)
            assert [entry.name for entry in app.entries] == ["inside.txt"]

    asyncio.run(exercise_app())
