#!/usr/bin/env python3
"""Validate a generated chatbot project without exposing secrets."""

from __future__ import annotations

import argparse
import ast
import os
import subprocess
import sys
from pathlib import Path


REQUIRED_FILES = (
    "app.py",
    "chatgpt_auth.py",
    "rag.py",
    "requirements.txt",
    "pyproject.toml",
    ".env.example",
    ".gitignore",
    ".streamlit/config.toml",
    "tests/test_rag.py",
    "tests/test_auth.py",
)


def project_python(project: Path) -> Path:
    windows = project / ".venv" / "Scripts" / "python.exe"
    posix = project / ".venv" / "bin" / "python"
    return windows if windows.exists() else posix


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Validate a document chatbot project")
    parser.add_argument("target", type=Path)
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    project = args.target.expanduser().resolve()

    missing = [name for name in REQUIRED_FILES if not (project / name).is_file()]
    if missing:
        print("Missing required files:", ", ".join(missing), file=sys.stderr)
        return 1

    for name in ("app.py", "chatgpt_auth.py", "rag.py", "tests/test_rag.py", "tests/test_auth.py"):
        source = (project / name).read_text(encoding="utf-8")
        ast.parse(source, filename=name)
    print("Python syntax: OK")

    ignored = (project / ".gitignore").read_text(encoding="utf-8")
    for required in (".env", ".streamlit/secrets.toml", ".venv/"):
        if required not in ignored:
            print(f".gitignore must include {required}", file=sys.stderr)
            return 1
    print("Secret and virtual-environment ignores: OK")

    for sensitive in (project / ".env", project / ".streamlit" / "secrets.toml"):
        if sensitive.exists():
            print(f"Note: {sensitive.name} exists locally and must never be committed.")

    if not args.skip_tests:
        python = project_python(project)
        if not python.exists():
            print("Virtual environment is missing; run bootstrap.py first.", file=sys.stderr)
            return 1
        environment = os.environ.copy()
        environment.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
        subprocess.run(
            [str(python), "-m", "pytest", "-q", "--basetemp", ".pytest-tmp"],
            cwd=project,
            env=environment,
            check=True,
        )
        print("Tests: OK")

    print("Project validation completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
