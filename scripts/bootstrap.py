#!/usr/bin/env python3
"""Create a ready-to-run document chatbot project from the bundled template."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path


MIN_PYTHON = (3, 11)


def venv_python(project: Path) -> Path:
    if sys.platform == "win32":
        return project / ".venv" / "Scripts" / "python.exe"
    return project / ".venv" / "bin" / "python"


def ensure_empty_target(target: Path) -> None:
    if target.exists() and any(target.iterdir()):
        raise SystemExit(
            f"Target directory is not empty: {target}\n"
            "Choose an empty directory so existing work is not overwritten."
        )
    target.mkdir(parents=True, exist_ok=True)


def run(command: list[str], cwd: Path) -> None:
    print("+", " ".join(command))
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
            "PIP_PROGRESS_BAR": "off",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        }
    )
    subprocess.run(command, cwd=cwd, env=environment, check=True)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(
        description="Scaffold and install the Streamlit document chatbot."
    )
    parser.add_argument("target", type=Path, help="Empty destination directory")
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Copy the template and create the virtual environment without downloading packages",
    )
    args = parser.parse_args()

    if sys.version_info < MIN_PYTHON:
        raise SystemExit("Python 3.11 or newer is required.")

    skill_root = Path(__file__).resolve().parents[1]
    template = skill_root / "assets" / "streamlit-rag-template"
    if not template.is_dir():
        raise SystemExit(f"Bundled template is missing: {template}")

    target = args.target.expanduser().resolve()
    ensure_empty_target(target)
    shutil.copytree(
        template,
        target,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(
            ".venv", "__pycache__", ".pytest_cache", ".pytest-tmp", "*.pyc"
        ),
    )
    print(f"Copied chatbot template to {target}")

    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    environment = target / ".venv"
    print(f"Creating virtual environment at {environment}")
    venv.EnvBuilder(with_pip=True).create(environment)
    python = venv_python(target)

    if not args.skip_install:
        run([str(python), "-m", "pip", "install", "--upgrade", "pip"], target)
        run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "-r",
                "requirements.txt",
                "pytest>=8.3,<10",
            ],
            target,
        )

    print("\nProject is ready.")
    print("Next: run scripts/check_project.py, then start Streamlit.")
    print("Local mode uses Continue with ChatGPT; hosted mode uses OPENAI_API_KEY.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
