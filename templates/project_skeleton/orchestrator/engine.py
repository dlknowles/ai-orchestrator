from __future__ import annotations

from typing import Iterable, List
from .steps.base import Step, Context


class Engine:
    """
    Orchestrates a sequence of Steps over a shared context.
    """

    def __init__(self, steps: Iterable[Step]) -> None:
        self.steps: List[Step] = list(steps)

    def run(self, initial_context: Context | None = None) -> Context:
        context: Context = initial_context or {}
        for step in self.steps:
            context = step.run(context)
            
        return context
