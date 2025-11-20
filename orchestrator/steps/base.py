from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


Context = Dict[str, Any]


class Step(ABC):
    """
    A single unit of work in a task.

    Each Step:
      - reads from the context
      - updates the context
      - returns the new context
    """

    name: str

    def __init__(self, name: str | None = None) -> None:
        # Allow override, otherwise use class name
        self.name = name or self.__class__.__name__

    @abstractmethod
    def run(self, context: Context) -> Context:
        raise NotImplementedError

    def __call__(self, context: Context) -> Context:
        return self.run(context)
