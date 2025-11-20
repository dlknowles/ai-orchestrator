from __future__ import annotations

from typing import Dict, Any
from orchestrator.engine import Engine
from orchestrator.steps.file_ops import LoadFile, WriteFile
from orchestrator.steps.base import Step, Context
from orchestrator.steps.llm_step import LLMStep


class UppercaseStep(Step):
    """
    Dummy transformation step:
    takes context["input_text"] and writes uppercased version to context["output_text"].
    """

    def __init__(self) -> None:
        super().__init__(name="UppercaseStep")

    def run(self, context: Context) -> Context:
        input_text = context.get("input_text")
        if input_text is None:
            raise KeyError("Expected 'input_text' in context.")
        
        context["output_text"] = str(input_text).upper()

        return context


def build_example_engine() -> Engine:
    system_prompt = (
        "You are a careful editor. "
        "You will take the input text and rewrite it for clarity and concision, "
        "preserving the original meaning."
    )
    
    steps = [
        LoadFile("examples/input.txt", context_key="input_text"),
        #UppercaseStep(),
        LLMStep(system_prompt=system_prompt, input_key="input_text", output_key="output_text"),
        WriteFile("examples/output.txt", context_key="output_text"),
    ]

    return Engine(steps)
