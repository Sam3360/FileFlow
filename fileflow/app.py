from __future__ import annotations

from pathlib import Path
from typing import Iterable

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, Label, ListItem, ListView, Static

from fileflow.filesystem import list_directory
from fileflow.models import FileEntry
from fileflow.operations import delete_selected, format_size


class FileFlowApp(App):
    CSS = """
    Screen {
        background: #0f172a;
        color: #e2e8f0;
    }
    #sidebar {
        width: 24;
        background: #111827;
        border: solid #1f2937;
    }
    #main {
        width: 1fr;
        background: #0b1120;
        border: solid #1f2937;
    }
    #status {
        height: 3;
        background: #111827;
        border: solid #1f2937;
    }
    Button {
        min-width: 12;
        margin: 0 1;
    }
    ListView {
        height: 1fr;
    }
    ListItem {
        padding: 0 1;
    }
    .selected {
        background: #312e81;
    }
    .focused {
        border: solid #67e8f9;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("f", "search", "Search"),
        ("c", "copy", "Copy"),
        ("m", "move", "Move"),
        ("p", "paste", "Paste"),
        ("n", "new_folder", "New folder"),
        ("d", "delete", "Delete"),
        ("h", "toggle_hidden", "Hidden"),
        ("\", "back", "Back"),
    ]

    current_path = reactive(str(Path.home()))
    show_hidden = reactive(False)
    selected = reactive([])
    status = reactive("Ready")

    def __init__(self):
        super().__init__()
        self.entries: list[FileEntry] = []
        self.current_index = 0
        self.search_focus = False

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
                yield Input(placeholder="Search files", id="search")
            with Vertical(id="main"):
                yield Static("Current directory", id="location")
                yield ListView(id="file-list")
            with Vertical(id="side-info"):
                yield Static("Details", id="details")
        yield Static(id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_directory()
        self.query_one("#search", Input).value = ""

    def refresh_directory(self) -> None:
        self.entries = list_directory(self.current_path, include_hidden=self.show_hidden)
        self.current_index = 0
        self.selected = []
        self.query_one("#location", Static).update(f"Location: {self.current_path}")
        self.render_entries()
        self.set_status(f"{len(self.entries)} items")

    def render_entries(self) -> None:
        file_list = self.query_one("#file-list", ListView)
        file_list.clear()
        for entry in self.entries:
            item = ListItem(Static(f"{entry.name}  {format_size(entry.size)}"))
            file_list.append(item)
        if file_list.index is not None:
            file_list.index = min(self.current_index, len(self.entries) - 1 if self.entries else 0)

    def set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)
        self.status = message

    def action_refresh(self) -> None:
        self.refresh_directory()

    def action_search(self) -> None:
        self.query_one("#search", Input).focus()

    def action_toggle_hidden(self) -> None:
        self.show_hidden = not self.show_hidden
        self.refresh_directory()

    def action_back(self) -> None:
        parent = Path(self.current_path).parent
        if parent.exists() and str(parent) != self.current_path:
            self.current_path = str(parent)
            self.refresh_directory()

    def action_copy(self) -> None:
        if self.entries:
            selected = self.entries[self.current_index]
            self.set_status(f"Copied {selected.name} to clipboard")

    def action_move(self) -> None:
        if self.entries:
            selected = self.entries[self.current_index]
            self.set_status(f"Moved {selected.name}")

    def action_paste(self) -> None:
        self.set_status("Paste action not implemented yet")

    def action_new_folder(self) -> None:
        self.set_status("New Folder action not implemented yet")

    def action_delete(self) -> None:
        if not self.entries:
            self.set_status("Nothing to delete")
            return
        selected = self.entries[self.current_index]
        errors = delete_selected([selected.path])
        if errors:
            self.set_status(errors[0])
        else:
            self.set_status(f"Deleted {selected.name}")
            self.refresh_directory()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        target_map = {
            "home": str(Path.home()),
            "desktop": str(Path.home() / "Desktop"),
            "documents": str(Path.home() / "Documents"),
            "downloads": str(Path.home() / "Downloads"),
            "pictures": str(Path.home() / "Pictures"),
            "thispc": str(Path.home().anchor or "."),
        }
        path = target_map.get(event.button.id)
        if path:
            self.current_path = path
            self.refresh_directory()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search":
            query = event.value.strip().lower()
            if not query:
                self.refresh_directory()
                return
            filtered = [entry for entry in self.entries if query in entry.name.lower()]
            self.entries = filtered
            self.render_entries()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if not self.entries:
            return
        self.current_index = event.list_view.index
        selected = self.entries[self.current_index]
        self.query_one("#details", Static).update(
            f"Name: {selected.name}\nPath: {selected.path}\nType: {'Folder' if selected.is_dir else 'File'}\nSize: {format_size(selected.size)}\nModified: {selected.modified.strftime('%Y-%m-%d %H:%M')}"
        )
        if selected.is_dir:
            self.current_path = str(selected.path)
            self.refresh_directory()


def main() -> None:
    app = FileFlowApp()
    app.run()
