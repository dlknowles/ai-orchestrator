from __future__ import annotations

from tasks.code_explainer_task import build_code_explainer_engine


def main() -> None:
    engine = build_code_explainer_engine()
    context = engine.run()
    print("Task 'code_explainer' completed. Context keys:", list(context.keys()))


if __name__ == "__main__":
    main()
