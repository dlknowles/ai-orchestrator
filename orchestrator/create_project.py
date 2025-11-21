from __future__ import annotations

import sys
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = REPO_ROOT / "templates" / "project_skeleton"


def create_project(project_name: str) -> None:
    project_dir = REPO_ROOT / ".." / project_name
    project_dir = project_dir.resolve()

    if project_dir.exists():
        raise FileExistsError(f"Project directory already exists: {project_dir}")

    shutil.copytree(TEMPLATE_DIR, project_dir)

    print(f"Created new project at: {project_dir}")
    print("Next steps:")
    print(f"  cd {project_dir.name}")
    print("  python -m venv .venv")
    print("  .venv\\Scripts\\activate  # or source .venv/bin/activate")
    print("  pip install -r requirements.txt")
    print("  python -m run_task")


def main(argv: list[str] | None = None) -> None:
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: python -m orchestrator.create_project <project_name>")
        sys.exit(1)

    project_name = argv[0]
    create_project(project_name)


if __name__ == "__main__":
    main()
