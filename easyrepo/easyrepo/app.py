"""Main Textual application for easyrepo."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from easyrepo.core import check_requirements
from easyrepo.screens.browser import BrowserScreen, DirectorySelected
from easyrepo.screens.wizard import WizardScreen


class EasyRepoApp(App):
    """easyrepo — Turn any folder into a GitHub repository."""

    TITLE = "easyrepo"
    SUB_TITLE = "Create a GitHub repo the easy way"
    CSS = """
    Screen {
        background: $surface;
    }

    #title {
        text-align: center;
        padding: 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    #path-display {
        padding: 0 1;
        color: $text-muted;
    }

    #tree-container {
        height: 1fr;
        border: solid $primary;
        margin: 1;
    }

    #button-row {
        height: auto;
        padding: 1;
        align: center middle;
    }

    #button-row Button {
        margin: 0 1;
    }

    #form {
        padding: 1 2;
        height: 1fr;
    }

    #form Label {
        margin-top: 1;
        text-style: bold;
    }

    #form Input {
        margin-bottom: 0;
    }

    #actions {
        height: auto;
        padding: 1;
        align: center middle;
    }

    #actions Button {
        margin: 0 1;
    }

    #status {
        padding: 1 2;
        height: auto;
    }

    #selected-path {
        padding: 1;
        background: $success-darken-2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("ctrl+c", "quit", "Quit", show=False),
    ]

    def on_mount(self) -> None:
        missing = check_requirements()
        if missing:
            self.notify(
                f"Missing requirements: {', '.join(missing)}\n"
                "Please install them and try again.",
                severity="error",
                timeout=10,
            )
        # Start with the browser
        self.push_screen(BrowserScreen(Path.cwd()))

    def on_directory_selected(self, message: DirectorySelected) -> None:
        """User picked a folder → go to wizard."""
        self.push_screen(WizardScreen(message.path))
