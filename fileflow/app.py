from __future__ import annotations

import os
import subprocess
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, ListItem, ListView, Static

from fileflow.clipboard import build_clipboard_state, copy_full_path_to_clipboard
from fileflow.filesystem import copy_item, create_directory, delete_path, list_directory, move_item
from fileflow.models import ClipboardState, FileEntry
from fileflow.operations import delete_selected, format_size, next_available_path


class NamePrompt(ModalScreen[str | None]):
    CSS = """
    NamePrompt {
        align: center middle;
    }
    #panel {
        width: 40;
        height: auto;
        padding: 1 2;
        border: solid #475569;
        background: #0f172a;
    }
    Input, Button {
        margin: 0 0 1 0;
    }
    """

    def __init__(self, title: str, default: str = "") -> None:
        super().__init__()
        self.title_text = title
        self.default = default

    def compose(self) -> ComposeResult:
        with Container(id="panel"):
            yield Static(self.title_text)
            yield Input(value=self.default, id="name-input")
            with Horizontal():
                yield Button("OK", id="ok", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            value = self.query_one("#name-input", Input).value.strip()
            self.dismiss(value or None)
        else:
            self.dismiss(None)


class FileFlowApp(App):
    CSS = """
    Screen {
        background: #0f172a;
        color: #e2e8f0;
    }
    #sidebar {
        width: 24;
        background: #111827;
        border: solid #475569;
        padding: 1;
    }
    #main {
        width: 1fr;
        background: #0b1120;
        border: solid #475569;
    }
    #status {
        height: 3;
        background: #111827;
        border: solid #475569;
        padding: 0 1;
    }
    Button {
        min-width: 12;
        margin: 0 0 1 0;
    }
    ListView {
        height: 1fr;
    }
    ListItem {
        padding: 0 1;
    }
    #details {
        padding: 1;
        background: #111827;
        border: solid #475569;
        height: 10;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "focus_search", "Search"),
        Binding("enter", "open_selected", "Open"),
        Binding("escape", "back", "Back"),
        Binding("ctrl+s", "toggle_hidden", "Hidden"),
        Binding("delete", "delete_selected", "Delete"),
        Binding("ctrl+n", "new_folder", "New folder"),
        Binding("c", "copy_selected", "Copy"),
        Binding("x", "cut_selected", "Cut"),
        Binding("v", "paste_selected", "Paste"),
        Binding("p", "properties", "Properties"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.current_path = str(Path.home())
        self.show_hidden = False
        self.entries: list[FileEntry] = []
        self.clipboard: ClipboardState = ClipboardState()
        self.current_index = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("Quick Access")
                yield Button("Home", id="home")
                yield Button("Desktop", id="desktop")
                yield Button("Documents", id="documents")
                yield Button("Downloads", id="downloads")
                yield Button("Pictures", id="pictures")
                yield Button("This PC", id="thispc")
                yield Button("Refresh", id="refresh")
                yield Button("Toggle hidden", id="toggle-hidden")
            with Vertical(id="main"):
                yield Static("Location", id="location")
                yield ListView(id="file-list")
            with Vertical(id="side-info"):
                yield Static("Details", id="details")
        yield Static(id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_directory()

    def _current_entry(self) -> FileEntry | None:
        if not self.entries:
            return None
        index = self.current_index
        if index < 0 or index >= len(self.entries):
            index = 0
        self.current_index = index
        return self.entries[index]

    def refresh_directory(self) -> None:
        self.entries = list_directory(self.current_path, include_hidden=self.show_hidden)
        self.current_index = 0
        self.query_one("#location", Static).update(f"Location: {self.current_path}")
        self.render_entries()
        self.set_status(f"{len(self.entries)} items")
        self.update_details()

    def render_entries(self) -> None:
        file_list = self.query_one("#file-list", ListView)
        file_list.clear()
        for entry in self.entries:
            label = f"{entry.name}  {format_size(entry.size)}"
            file_list.append(ListItem(Static(label)))
        if self.entries:
            file_list.index = self.current_index
        else:
            file_list.index = None

    def set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def update_details(self) -> None:
        entry = self._current_entry()
        if entry is None:
            self.query_one("#details", Static).update("No item selected")
            return
        self.query_one("#details", Static).update(
            "\n".join(
                [
                    f"Name: {entry.name}",
                    f"Path: {entry.path}",
                    f"Type: {'Folder' if entry.is_dir else 'File'}",
                    f"Size: {format_size(entry.size)}",
                    f"Modified: {entry.modified.strftime('%Y-%m-%d %H:%M')}",
                ]
            )
        )

    def action_refresh(self) -> None:
        self.refresh_directory()

    def action_focus_search(self) -> None:
        self.set_status("Search is available in the file list filter; use the search box in the sidebar when implemented.")

    def action_toggle_hidden(self) -> None:
        self.show_hidden = not self.show_hidden
        self.refresh_directory()

    def action_back(self) -> None:
        if self.current_path == str(Path.home().anchor):
            return
        parent = Path(self.current_path).parent
        if parent.exists() and str(parent) != self.current_path:
            self.current_path = str(parent)
            self.refresh_directory()

    def action_open_selected(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        if entry.is_dir:
            self.current_path = str(entry.path)
            self.refresh_directory()
            return
        try:
            os.startfile(str(entry.path))
            self.set_status(f"Opened {entry.name}")
        except OSError as exc:
            self.set_status(f"Could not open file: {exc}")

    def action_copy_selected(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        self.clipboard = build_clipboard_state([entry.path], "copy")
        self.set_status(f"Copied {entry.name} to clipboard")

    def action_cut_selected(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        self.clipboard = build_clipboard_state([entry.path], "move")
        self.set_status(f"Cut {entry.name}")

    async def action_paste_selected(self) -> None:
        if not self.clipboard.paths:
            self.set_status("Clipboard is empty")
            return
        source_paths = list(self.clipboard.paths)
        for source in source_paths:
            source_path = Path(source)
            destination = Path(self.current_path) / source_path.name
            if destination.exists():
                destination = next_available_path(destination)
            try:
                if self.clipboard.mode == "copy":
                    copy_item(source_path, destination)
                else:
                    move_item(source_path, destination)
            except OSError as exc:
                self.set_status(f"Paste failed: {exc}")
                return
        self.refresh_directory()
        self.set_status("Pasted clipboard contents")

    async def action_new_folder(self) -> None:
        result = await self.push_screen_wait(NamePrompt("New folder name"))
        if not result:
            return
        name = str(result).strip()
        if not name:
            self.set_status("Folder name cannot be blank")
            return
        target = Path(self.current_path) / name
        if target.exists():
            self.set_status("Folder already exists")
            return
        try:
            create_directory(target)
            self.refresh_directory()
            self.set_status(f"Created {name}")
        except OSError as exc:
            self.set_status(f"Could not create folder: {exc}")

    async def action_rename(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        result = await self.push_screen_wait(NamePrompt("Rename item", default=entry.name))
        if not result or result == entry.name:
            return
        try:
            target = entry.path.with_name(str(result))
            if target.exists():
                raise FileExistsError(f"Destination exists: {target}")
            entry.path.rename(target)
            self.refresh_directory()
            self.set_status(f"Renamed to {result}")
        except OSError as exc:
            self.set_status(f"Rename failed: {exc}")

    async def action_delete_selected(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        try:
            delete_path(entry.path)
            self.refresh_directory()
            self.set_status(f"Deleted {entry.name}")
        except OSError as exc:
            self.set_status(f"Delete failed: {exc}")

    def action_properties(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        self.set_status(f"Properties: {entry.path} | size={format_size(entry.size)}")
        copy_full_path_to_clipboard(entry.path)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        target_map = {
            "home": str(Path.home()),
            "desktop": str(Path.home() / "Desktop"),
            "documents": str(Path.home() / "Documents"),
            "downloads": str(Path.home() / "Downloads"),
            "pictures": str(Path.home() / "Pictures"),
            "thispc": str(Path.home().anchor or "."),
            "refresh": None,
            "toggle-hidden": None,
        }
        if event.button.id == "refresh":
            self.refresh_directory()
            return
        if event.button.id == "toggle-hidden":
            self.action_toggle_hidden()
            return
        path = target_map.get(event.button.id)
        if path:
            self.current_path = path
            self.refresh_directory()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.current_index = event.list_view.index if event.list_view.index is not None else 0
        self.update_details()

    def on_list_view_key(self, event: ListView.Key) -> None:
        if event.key == "enter":
            self.action_open_selected()


def main() -> None:
    app = FileFlowApp()
    app.run()
