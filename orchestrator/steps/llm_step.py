from __future__ import annotations

from orchestrator.steps.base import Step, Context
from orchestrator.llm import complete


class LLMStep(Step):
    """
    Generic LLM-powered transformation step.
    Reads from context[input_key], writes result to context[output_key].
    """

    def __init__(self, system_prompt: str, input_key: str = "input_text", output_key: str = "output_text") -> None:
        super().__init__(name="LLMStep")
        self.system_prompt = system_prompt
        self.input_key = input_key
        self.output_key = output_key

    def run(self, context: Context) -> Context:
        if self.input_key not in context:
            raise KeyError(
                f"Expected '{self.input_key}' in context. "
                f"Available keys: {list(context.keys())}"
            )

        user_text = str(context[self.input_key])
        result = complete(
            prompt=user_text,
            system_prompt=self.system_prompt,
        )
        context[self.output_key] = result

        return context
