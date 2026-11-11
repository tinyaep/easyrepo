"""Directory browser screen."""

from __future__ import annotations

from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import DirectoryTree, Footer, Header, Label, Static, Button


class DirectorySelected(Message):
    """Message sent when user selects a directory."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__()


class BrowserScreen(Screen):
    """Simple file browser that lets the user pick a folder."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("s", "select", "Select folder"),
        Binding("backspace", "go_up", "Go up"),
        Binding("enter", "enter_or_select", "Open / Select"),
    ]

    def __init__(self, start_path: Path | None = None) -> None:
        super().__init__()
        self.start_path = start_path or Path.cwd()
        self.current_path = self.start_path.resolve()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static(
            "[bold]easyrepo[/] — Choose the folder you want to turn into a GitHub repository",
            id="title",
        )
        yield Static(f"Current: {self.current_path}", id="path-display")
        with Container(id="tree-container"):
            yield DirectoryTree(str(self.current_path), id="dir-tree")
        with Horizontal(id="button-row"):
            yield Button("Select this folder", variant="primary", id="btn-select")
            yield Button("Go up", id="btn-up")
            yield Button("Quit", variant="error", id="btn-quit")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#dir-tree", DirectoryTree).focus()

    def _update_path_display(self) -> None:
        self.query_one("#path-display", Static).update(f"Current: {self.current_path}")

    @on(DirectoryTree.DirectorySelected)
    def on_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """When user expands/selects a directory in the tree."""
        self.current_path = event.path
        self._update_path_display()

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        # If they click a file, just select its parent folder
        self.current_path = event.path.parent
        self._update_path_display()

    def action_select(self) -> None:
        self.post_message(DirectorySelected(self.current_path))

    def action_go_up(self) -> None:
        parent = self.current_path.parent
        if parent != self.current_path:
            self.current_path = parent
            tree = self.query_one("#dir-tree", DirectoryTree)
            tree.path = self.current_path
            tree.reload()
            self._update_path_display()

    def action_enter_or_select(self) -> None:
        # Simple behavior: select current
        self.action_select()

    def action_quit(self) -> None:
        self.app.exit()

    @on(Button.Pressed, "#btn-select")
    def on_select_button(self) -> None:
        self.action_select()

    @on(Button.Pressed, "#btn-up")
    def on_up_button(self) -> None:
        self.action_go_up()

    @on(Button.Pressed, "#btn-quit")
    def on_quit_button(self) -> None:
        self.action_quit()
