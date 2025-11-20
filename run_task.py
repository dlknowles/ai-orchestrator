from __future__ import annotations

from tasks.example_task import build_example_engine


def main() -> None:
    engine = build_example_engine()
    context = engine.run()
    print("Task completed.")
    print("Final context keys:", list(context.keys()))


if __name__ == "__main__":
    main()
