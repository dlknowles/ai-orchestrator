import os
import requests

class LMStudioClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self.base_url = base_url or os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
        self.model = model or os.getenv("LMSTUDIO_MODEL", "qwen/qwen3-coder-30b")  # your model
        self.api_key = api_key or os.getenv("LMSTUDIO_API_KEY", "lm-studio")
        # total timeout, but we’ll split into connect + read below
        self.timeout_seconds = timeout_seconds or int(os.getenv("LMSTUDIO_TIMEOUT_SEC", "600"))
        # 600 seconds = 10 minutes, overkill but safe for big local models

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload: dict[str, object] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            # timeout=(connect_timeout, read_timeout)
            resp = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=(10, self.timeout_seconds),
            )
        except requests.exceptions.ReadTimeout as e:
            raise RuntimeError(
                f"LM Studio timed out after {self.timeout_seconds}s. "
                "The local model may be too slow or still loading. "
                "Try lowering model size, ensuring the model is fully loaded, "
                "or increasing LMSTUDIO_TIMEOUT_SEC."
            ) from e

        resp.raise_for_status()
        data = resp.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Unexpected LM Studio response: {data}") from exc
