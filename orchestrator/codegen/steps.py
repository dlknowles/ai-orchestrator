from __future__ import annotations
from pathlib import Path
from typing import Protocol
from .context import CodegenContext
from .llm_client import LMStudioClient


class Step(Protocol):
    def run(self, ctx: CodegenContext) -> None: ...


class LoadProjectSpecStep:
    def run(self, ctx: CodegenContext) -> None:
        ctx.ensure_project_exists()
        ctx.ensure_spec_exists()

        ctx.spec_text = ctx.spec_path.read_text(encoding="utf-8")


class GenerateComponentStep:
    """
    Calls LM Studio to create a complete TSX/TS file for the target.
    """

    def __init__(self, llm: LMStudioClient | None = None) -> None:
        self.llm = llm or LMStudioClient()

    def run(self, ctx: CodegenContext) -> None:
        if ctx.spec_text is None:
            raise ValueError("spec_text is not loaded. Run LoadProjectSpecStep first.")

        target_path: Path = ctx.target_file
        # MVP assumption: Vite + React + TypeScript,
        # target is something like src/App.tsx or src/main.tsx
        system_prompt = (
            "You are an expert React + TypeScript code generator. "
            "You receive a high-level project spec and must generate a single complete source file for `{target_path}` in a Vite + React + TypeScript project.\n\n"
            "Requirements:\n"
            "- Output ONLY the raw file contents. No backticks, no markdown, no comments outside the code.\n"
            "- Assume React 18 and Vite standard layout.\n"
            "- The file must be valid TypeScript/TSX and compile without modification.\n"
            "- Do not add explanations, just the code.\n"
        )

        user_prompt = (
            f"# Project Spec\n\n"
            f"{ctx.spec_text}\n\n"
            f"# Target file\n"
            f"- Project root: {ctx.project_path}\n"
            f"- File to generate or overwrite: {target_path}\n\n"
            "Generate ONLY the contents for this file."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        code = self.llm.chat_completion(
            messages=messages,
            temperature=0.0,   # deterministic-ish
            max_tokens=4096,
        )

        # Some models still sneak in backticks. Strip common wrappers defensively.
        cleaned = self._strip_fence(code)
        ctx.generated_code = cleaned

    @staticmethod
    def _strip_fence(text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```"):
            # Remove leading ```... and trailing ```
            lines = stripped.splitlines()
            # Drop first line (``` or ```tsx/ts)
            lines = lines[1:]
            # Drop final ``` if present
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            stripped = "\n".join(lines).strip()
        return stripped


class WriteGeneratedFileStep:
    def run(self, ctx: CodegenContext) -> None:
        if ctx.generated_code is None:
            raise ValueError("generated_code is not set. Run GenerateComponentStep first.")

        abs_target = ctx.abs_target_file
        abs_target.parent.mkdir(parents=True, exist_ok=True)
        abs_target.write_text(ctx.generated_code, encoding="utf-8")
        # MVP: direct overwrite. No diff/merge.
