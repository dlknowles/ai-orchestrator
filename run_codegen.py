from __future__ import annotations
import argparse
from pathlib import Path
import sys
from orchestrator.codegen.task import CodegenTask


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Project-aware codegen MVP for ai-orchestrator (local LM Studio)."
    )
    parser.add_argument(
        "--project-path",
        required=True,
        help="Path to existing Vite+TS project root.",
    )
    parser.add_argument(
        "--spec-path",
        required=True,
        help="Path to markdown spec file (e.g., spec.md).",
    )
    parser.add_argument(
        "--target-file",
        default="src/App.tsx",
        help="Target file path relative to project root. Default: src/App.tsx",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    project_path = Path(args.project_path).resolve()
    spec_path = Path(args.spec_path).resolve()
    target_file = Path(args.target_file)

    task = CodegenTask(
        project_path=project_path,
        spec_path=spec_path,
        target_file=target_file,
    )
    task.run()

    print(f"[codegen] Wrote {target_file} in {project_path}")


if __name__ == "__main__":
    main(sys.argv[1:])
