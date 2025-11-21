from __future__ import annotations

from orchestrator.engine import Engine
from orchestrator.steps.file_ops import LoadFile, WriteFile
from orchestrator.steps.llm_step import LLMStep


def build_code_explainer_engine() -> Engine:
    """Engine for the 'code_explainer' task.

    Customize:
      - system_prompt
      - input/output file paths
      - any additional steps you want to chain
    """
    system_prompt = (
        "You are an AI assistant. "
        "Rewrite the input text clearly and concisely. "
        "Do NOT invent new facts or add information not present in the input."
    )

    steps = [
        LoadFile("examples/code_explainer_input.txt", context_key="input_text"),
        LLMStep(
            system_prompt=system_prompt,
            input_key="input_text",
            output_key="output_text",
        ),
        WriteFile("examples/code_explainer_output.txt", context_key="output_text"),
    ]

    return Engine(steps)
