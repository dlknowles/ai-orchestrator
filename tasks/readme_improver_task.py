from orchestrator.engine import Engine
from orchestrator.steps.file_ops import LoadFile, WriteFile
from orchestrator.steps.llm_step import LLMStep


def build_readme_improver_engine() -> Engine:
    system_prompt = (
        "You are a senior engineer improving README files.\n"
        "Rewrite the input to be clearer, better structured, and more professional.\n"
        "CRITICAL CONSTRAINTS:\n"
        "- Do NOT invent features, components, or capabilities that are not present in the input.\n"
        "- Do NOT claim the existence of additional documentation or APIs unless explicitly mentioned.\n"
        "- Only use information from the input text; you may reorganize, rephrase, and format it.\n"
    )


    steps = [
        LoadFile("examples/README_input.md", context_key="input_text"),
        LLMStep(system_prompt=system_prompt, input_key="input_text", output_key="output_text"),
        WriteFile("examples/README_output.md", context_key="output_text"),
    ]

    return Engine(steps)
