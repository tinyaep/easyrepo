"""Core logic: git operations + GitHub repo creation via `gh` CLI."""

from __future__ import annotations

import subprocess
import shutil
from pathlib import Path
from typing import Optional


class EasyRepoError(Exception):
    """Base error for easyrepo operations."""


def check_requirements() -> list[str]:
    """Return a list of missing requirements."""
    missing = []
    if not shutil.which("git"):
        missing.append("git")
    if not shutil.which("gh"):
        missing.append("gh (GitHub CLI) — install from https://cli.github.com")
    return missing


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise EasyRepoError(
            f"Command failed: {' '.join(cmd)}\n{result.stderr.strip()}"
        )
    return result


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def detect_language(path: Path) -> Optional[str]:
    """Very simple language detection based on common files."""
    files = {p.name.lower() for p in path.iterdir() if p.is_file()}

    if "package.json" in files or "pnpm-lock.yaml" in files or "yarn.lock" in files:
        return "Node"
    if "requirements.txt" in files or "pyproject.toml" in files or "setup.py" in files:
        return "Python"
    if "cargo.toml" in files:
        return "Rust"
    if "go.mod" in files:
        return "Go"
    if "pom.xml" in files or "build.gradle" in files:
        return "Java"
    if any(f.endswith(".csproj") for f in files):
        return "C#"
    if "composer.json" in files:
        return "PHP"
    if "gemfile" in files:
        return "Ruby"
    return None


# Common gitignore templates (short versions for beginners)
GITIGNORE_TEMPLATES = {
    "Python": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.env
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
""",
    "Node": """# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
dist/
build/
.env
.env.local
.DS_Store
""",
    "Rust": """# Rust
/target/
**/*.rs.bk
Cargo.lock
""",
    "Go": """# Go
bin/
*.exe
*.test
*.out
vendor/
""",
    "Java": """# Java
*.class
*.jar
*.war
target/
.idea/
*.iml
""",
    "Generic": """# Generic
.DS_Store
Thumbs.db
*.log
.env
.env.local
.vscode/
.idea/
""",
}


LICENSE_TEXTS = {
    "MIT": """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
    "Apache-2.0": """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Copyright (c) {year} {author}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
""",
    "GPL-3.0": """GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (c) {year} {author}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
""",
    "None": None,
}


def create_gitignore(path: Path, language: Optional[str]) -> None:
    gitignore_path = path / ".gitignore"
    if gitignore_path.exists():
        return  # don't overwrite

    content = GITIGNORE_TEMPLATES.get(language or "Generic", GITIGNORE_TEMPLATES["Generic"])
    gitignore_path.write_text(content, encoding="utf-8")


def create_license(path: Path, license_id: str, author: str = "") -> None:
    if license_id == "None" or license_id not in LICENSE_TEXTS:
        return

    from datetime import datetime
    year = str(datetime.now().year)
    text = LICENSE_TEXTS[license_id].format(year=year, author=author or "Your Name")
    (path / "LICENSE").write_text(text, encoding="utf-8")


def create_readme(path: Path, name: str, description: str) -> None:
    readme_path = path / "README.md"
    if readme_path.exists():
        return

    content = f"""# {name}

{description}

## Getting Started

TODO: Add installation and usage instructions.

## License

See the LICENSE file for details.
"""
    readme_path.write_text(content, encoding="utf-8")


def create_repo(
    path: Path,
    name: str,
    description: str,
    private: bool,
    license_id: str,
    add_readme: bool,
    add_gitignore: bool,
    author: str = "",
) -> str:
    """
    Full workflow:
    1. Prepare files (gitignore, license, readme)
    2. git init (if needed)
    3. git add + commit
    4. gh repo create + push
    Returns the GitHub URL.
    """
    path = path.resolve()

    # 1. Prepare files
    language = detect_language(path) if add_gitignore else None
    if add_gitignore:
        create_gitignore(path, language)

    if license_id and license_id != "None":
        create_license(path, license_id, author)

    if add_readme:
        create_readme(path, name, description)

    # 2. Git init
    if not is_git_repo(path):
        run(["git", "init", "-b", "main"], cwd=path)

    # 3. First commit
    run(["git", "add", "."], cwd=path)
    # Only commit if there is something to commit
    status = run(["git", "status", "--porcelain"], cwd=path, check=False)
    if status.stdout.strip():
        run(["git", "commit", "-m", "Initial commit"], cwd=path)

    # 4. Create on GitHub + push
    visibility = "--private" if private else "--public"

    cmd = [
        "gh", "repo", "create", name,
        visibility,
        "--source", str(path),
        "--remote", "origin",
        "--push",
    ]
    if description:
        cmd.extend(["--description", description])

    result = run(cmd, cwd=path)

    # Try to extract the URL from output
    # gh usually prints: ✓ Created repository user/name on GitHub
    url = f"https://github.com/{name}"  # fallback
    for line in (result.stdout + result.stderr).splitlines():
        if "github.com" in line.lower() and ("http" in line or "https" in line):
            # crude extraction
            for part in line.split():
                if "github.com" in part:
                    url = part.strip().rstrip(".")
                    break

    return url
