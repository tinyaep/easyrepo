"""Wizard screen: ask for repo details then run the creation."""

from __future__ import annotations

from pathlib import Path

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    RadioButton,
    RadioSet,
    Checkbox,
    Static,
    LoadingIndicator,
)
from textual.validation import Length

from easyrepo.core import create_repo, EasyRepoError, detect_language


class WizardScreen(Screen):
    """Collect options and create the repository."""

    def __init__(self, project_path: Path) -> None:
        super().__init__()
        self.project_path = project_path.resolve()
        self.detected_lang = detect_language(self.project_path)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)

        with VerticalScroll(id="form"):
            yield Static(
                f"[bold green]Selected folder:[/] {self.project_path}",
                id="selected-path",
            )
            yield Static("")

            yield Label("Repository name")
            yield Input(
                value=self.project_path.name,
                placeholder="my-awesome-project",
                id="name",
                validators=[Length(minimum=1, maximum=100)],
            )

            yield Label("Description (optional)")
            yield Input(
                placeholder="A short description of your project",
                id="description",
            )

            yield Label("Visibility")
            with RadioSet(id="visibility"):
                yield RadioButton("Public", value=True, id="vis-public")
                yield RadioButton("Private", id="vis-private")

            yield Label("License")
            with RadioSet(id="license"):
                yield RadioButton("MIT (recommended for most projects)", value=True, id="lic-mit")
                yield RadioButton("Apache-2.0", id="lic-apache")
                yield RadioButton("GPL-3.0", id="lic-gpl")
                yield RadioButton("No license", id="lic-none")

            yield Static("")
            yield Checkbox("Create a basic README.md", value=True, id="add-readme")
            yield Checkbox(
                f"Add .gitignore" + (f" (detected: {self.detected_lang})" if self.detected_lang else ""),
                value=True,
                id="add-gitignore",
            )

            yield Static("")
            yield Label("Your name (for the license file)")
            yield Input(placeholder="Your Name", id="author")

        with Horizontal(id="actions"):
            yield Button("← Back", id="btn-back")
            yield Button("Create repository 🚀", variant="success", id="btn-create")

        yield Footer()
        yield Static("", id="status")

    def on_mount(self) -> None:
        self.query_one("#name", Input).focus()

    @on(Button.Pressed, "#btn-back")
    def on_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-create")
    def on_create(self) -> None:
        self.run_create()

    @work(thread=True)
    def run_create(self) -> None:
        name = self.query_one("#name", Input).value.strip()
        description = self.query_one("#description", Input).value.strip()
        author = self.query_one("#author", Input).value.strip()

        if not name:
            self.app.call_from_thread(
                self.query_one("#status", Static).update,
                "[red]Repository name is required[/]",
            )
            return

        # Visibility
        vis_set = self.query_one("#visibility", RadioSet)
        private = vis_set.pressed_button and vis_set.pressed_button.id == "vis-private"

        # License
        lic_set = self.query_one("#license", RadioSet)
        license_map = {
            "lic-mit": "MIT",
            "lic-apache": "Apache-2.0",
            "lic-gpl": "GPL-3.0",
            "lic-none": "None",
        }
        license_id = "MIT"
        if lic_set.pressed_button:
            license_id = license_map.get(lic_set.pressed_button.id, "MIT")

        add_readme = self.query_one("#add-readme", Checkbox).value
        add_gitignore = self.query_one("#add-gitignore", Checkbox).value

        # Disable button + show status
        self.app.call_from_thread(
            self.query_one("#btn-create", Button).update,
            "Creating… please wait",
        )
        self.app.call_from_thread(
            self.query_one("#status", Static).update,
            "[yellow]Working… creating repository on GitHub…[/]",
        )

        try:
            url = create_repo(
                path=self.project_path,
                name=name,
                description=description,
                private=private,
                license_id=license_id,
                add_readme=add_readme,
                add_gitignore=add_gitignore,
                author=author,
            )
            self.app.call_from_thread(
                self.query_one("#status", Static).update,
                f"[bold green]✓ Success![/]\n\nRepository created:\n[link]{url}[/link]",
            )
            self.app.call_from_thread(
                self.query_one("#btn-create", Button).update,
                "Done!",
            )
            # Optionally open browser
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception:
                pass

        except EasyRepoError as e:
            self.app.call_from_thread(
                self.query_one("#status", Static).update,
                f"[bold red]Error:[/]\n{e}",
            )
            self.app.call_from_thread(
                self.query_one("#btn-create", Button).update,
                "Create repository 🚀",
            )
        except Exception as e:
            self.app.call_from_thread(
                self.query_one("#status", Static).update,
                f"[bold red]Unexpected error:[/]\n{e}",
            )
            self.app.call_from_thread(
                self.query_one("#btn-create", Button).update,
                "Create repository 🚀",
            )
