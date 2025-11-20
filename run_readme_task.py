# run_readme_task.py
from tasks.readme_improver_task import build_readme_improver_engine


def main() -> None:
    engine = build_readme_improver_engine()
    context = engine.run()
    print("README improvement completed. Keys:", list(context.keys()))


if __name__ == "__main__":
    main()
