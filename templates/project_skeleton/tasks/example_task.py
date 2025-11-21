from orchestrator.engine import Engine
from orchestrator.steps.file_ops import LoadFile, WriteFile
from orchestrator.steps.llm_step import LLMStep


def build_example_engine() -> Engine:
    system_prompt = (
        "Rewrite the input text clearly and concisely. "
        "Do NOT invent new facts or add information not in the input."
    )

    steps = [
        LoadFile("examples/input.txt", "input_text"),
        LLMStep(system_prompt, "input_text", "output_text"),
        WriteFile("examples/output.txt", "output_text"),
    ]

    return Engine(steps)
