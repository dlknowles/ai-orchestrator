from __future__ import annotations

from typing import List
from openai import OpenAI


# Adjust this model name to whatever LM Studio is serving
DEFAULT_MODEL_NAME = "qwen/qwen3-coder-30b"  # e.g. from LM Studio Server panel


def get_client() -> OpenAI:
    """
    Return an OpenAI-compatible client pointing at the LM Studio local server.
    """

    return OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",  # LM Studio ignores this but it must be non-empty
    )


def complete(prompt: str, system_prompt: str | None = None, model: str | None = None) -> str:
    """
    Single-turn completion using the local LM Studio model.
    """

    client = get_client()
    model_name = model or DEFAULT_MODEL_NAME
    messages: List[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.2,
    )
    
    return response.choices[0].message.content or ""
