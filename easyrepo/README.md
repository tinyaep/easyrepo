# easyrepo

**Turn any folder into a GitHub repository in seconds — with a beautiful terminal UI.**

Perfect for beginners. No more memorizing `git init`, `git remote add`, `gh repo create`, etc.

## What it does

1. You run `easyrepo`
2. A terminal file browser opens
3. Navigate to the folder that contains your project
4. Select it
5. Answer a few simple questions (name, description, public/private, license, README…)
6. `easyrepo` does **everything** for you:
   - Initializes git (if needed)
   - Creates a proper `.gitignore`
   - Adds a license file
   - Creates a README (optional)
   - Creates the repository on GitHub
   - Makes the first commit
   - Pushes everything
   - Opens the repo in your browser

## Requirements

- Python 3.10+
- [GitHub CLI (`gh`)](https://cli.github.com/) installed and logged in (`gh auth login`)
- Git

## Installation

```bash
# Clone the repo (once you push it)
git clone https://github.com/YOUR_USERNAME/easyrepo.git
cd easyrepo

# Install
pip install -e .

# Or just run without installing
pip install textual
python -m easyrepo
```

## Usage

```bash
easyrepo
```

That's it. The TUI will open.

### Keyboard shortcuts (file browser)

| Key        | Action                  |
|------------|-------------------------|
| `↑` / `↓`  | Move up/down            |
| `Enter`    | Open folder / Select    |
| `Backspace`| Go up one directory     |
| `s`        | Select current folder   |
| `q`        | Quit                    |

## Features

- Beautiful terminal UI built with [Textual](https://textual.textualize.io/)
- Interactive directory browser
- Smart defaults (repo name = folder name)
- License picker with short explanations
- Automatic language detection for `.gitignore`
- Optional README generation
- Uses official `gh` CLI under the hood (secure + reliable)
- Beginner-friendly explanations while it works

## Project structure

```
easyrepo/
├── easyrepo/
│   ├── __init__.py
│   ├── __main__.py
│   ├── app.py              # Main Textual application
│   ├── screens/
│   │   ├── browser.py      # File/folder browser
│   │   └── wizard.py       # Questions + confirmation
│   └── core.py             # Git + GitHub logic
├── pyproject.toml
└── README.md
```

## License

MIT
