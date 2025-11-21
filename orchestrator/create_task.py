from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
EXAMPLES_DIR = REPO_ROOT / "examples"


def to_snake_case(name: str) -> str:
    """
    Very simple normalization: lowercase, spaces and dashes -> underscores.
    """
    return name.strip().replace(" ", "_").replace("-", "_").lower()


def generate_task_files(task_name_raw: str) -> None:
    task_slug = to_snake_case(task_name_raw)

    task_module_name = f"{task_slug}_task"
    task_builder_name = f"build_{task_slug}_engine"

    task_file_path = TASKS_DIR / f"{task_module_name}.py"
    runner_file_path = REPO_ROOT / f"run_{task_slug}.py"
    input_file_path = EXAMPLES_DIR / f"{task_slug}_input.txt"

    if task_file_path.exists() or runner_file_path.exists():
        raise FileExistsError(
            f"Task or runner already exists for '{task_slug}'. "
            f"Task: {task_file_path}, Runner: {runner_file_path}"
        )

    # Ensure directories exist
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    # --- Task file template ---
    task_template = dedent(
        f"""
        from __future__ import annotations

        from orchestrator.engine import Engine
        from orchestrator.steps.file_ops import LoadFile, WriteFile
        from orchestrator.steps.llm_step import LLMStep


        def {task_builder_name}() -> Engine:
            \"\"\"Engine for the '{task_slug}' task.

            Customize:
              - system_prompt
              - input/output file paths
              - any additional steps you want to chain
            \"\"\"
            system_prompt = (
                "You are an AI assistant. "
                "Rewrite the input text clearly and concisely. "
                "Do NOT invent new facts or add information not present in the input."
            )

            steps = [
                LoadFile("examples/{task_slug}_input.txt", context_key="input_text"),
                LLMStep(
                    system_prompt=system_prompt,
                    input_key="input_text",
                    output_key="output_text",
                ),
                WriteFile("examples/{task_slug}_output.txt", context_key="output_text"),
            ]

            return Engine(steps)
        """
    ).lstrip()

    # --- Runner file template ---
    runner_template = dedent(
        f"""
        from __future__ import annotations

        from tasks.{task_module_name} import {task_builder_name}


        def main() -> None:
            engine = {task_builder_name}()
            context = engine.run()
            print("Task '{task_slug}' completed. Context keys:", list(context.keys()))


        if __name__ == "__main__":
            main()
        """
    ).lstrip()

    # --- Input file template ---
    input_template = (
        "This is a placeholder input for the "
        f"'{task_slug}' task. Replace this with real content.\n"
    )

    # Write files
    task_file_path.write_text(task_template, encoding="utf-8")
    runner_file_path.write_text(runner_template, encoding="utf-8")
    input_file_path.write_text(input_template, encoding="utf-8")

    print(f"Created task:   {task_file_path}")
    print(f"Created runner: {runner_file_path}")
    print(f"Created input:  {input_file_path}")


def main(argv: list[str] | None = None) -> None:
    argv = argv or sys.argv[1:]

    if not argv:
        print("Usage: python -m orchestrator.create_task <task_name>")
        sys.exit(1)

    task_name_raw = " ".join(argv)
    generate_task_files(task_name_raw)


if __name__ == "__main__":
    main()
