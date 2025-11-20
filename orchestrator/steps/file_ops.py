from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from .base import Step, Context


class LoadFile(Step):
    """
    Load a text file into context["input_text"].
    """

    def __init__(self, source_path: str | Path, context_key: str = "input_text") -> None:
        super().__init__(name="LoadFile")
        self.source_path = Path(source_path)
        self.context_key = context_key

    def run(self, context: Context) -> Context:
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source file not found: {self.source_path}")

        text = self.source_path.read_text(encoding="utf-8")
        context[self.context_key] = text
        return context


class WriteFile(Step):
    """
    Write context[context_key] to a file at target_path.
    """

    def __init__(self, target_path: str | Path, context_key: str = "output_text") -> None:
        super().__init__(name="WriteFile")
        self.target_path = Path(target_path)
        self.context_key = context_key

    def run(self, context: Context) -> Context:
        if self.context_key not in context:
            raise KeyError(
                f"Context key '{self.context_key}' not found. "
                f"Available keys: {list(context.keys())}"
            )

        self.target_path.parent.mkdir(parents=True, exist_ok=True)
        self.target_path.write_text(str(context[self.context_key]), encoding="utf-8")
        return context
