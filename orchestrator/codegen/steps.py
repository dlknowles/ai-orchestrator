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
    The model is treated strictly as a code printer for a single file.
    """

    def __init__(self, llm: LMStudioClient | None = None) -> None:
        self.llm = llm or LMStudioClient()

    def run(self, ctx: CodegenContext) -> None:
        if ctx.spec_text is None:
            raise ValueError("spec_text is not loaded. Run LoadProjectSpecStep first.")

        target_path: Path = ctx.target_file

        # 1) SYSTEM PROMPT: strict contract
        system_prompt = (
            "You are an expert React + TypeScript code generator running inside an automated tool. "
            "You MUST obey the following rules exactly:\n\n"
            "1. You generate the contents of ONE AND ONLY ONE file.\n"
            f"   - Target file path (relative to project root): {target_path}\n"
            "   - The project is a Vite + React + TypeScript + Tailwind CSS project.\n"
            "2. Output MUST be valid TypeScript/TSX code that compiles without edits.\n"
            "   - Do NOT include markdown, backticks, fences, or explanations.\n"
            "   - Do NOT include comments outside the code.\n"
            "   - Do NOT mention that you are an AI or describe what you are doing.\n"
            "3. No extra files or imports:\n"
            "   - Do NOT assume any files other than the default Vite React TS template.\n"
            "   - Do NOT import from files that do not already exist.\n"
            "   - Do NOT add routing libraries, state libraries, or CSS files.\n"
            "   - Use only React, TypeScript, and Tailwind utility classes.\n"
            "4. TAILWIND RULES (strict):\n"
            "    - You may only use valid Tailwind classes from the default Tailwind CSS palette.\n"
            "    - You MUST NOT invent color shades (e.g., bg-slate-750, bg-slate-850).\n"
            "    - Allowed slate shades are ONLY: 50, 100, 200, 300, 400, 500, 600, 700, 800, 900.\n"
            "    - Allowed variants must match Tailwind defaults (hover:, focus:, active:, etc.).\n"
            "    - Do NOT use any class that Tailwind does not ship with by default.\n"
            "5. Functional + typed React:\n"
            "   - Use function components and hooks only (no class components).\n"
            "   - Define appropriate TypeScript types for props and data structures.\n"
            "6. Structure for this particular file (strongly preferred):\n"
            "   - Define Task and TaskStep types.\n"
            "   - Define a hard-coded array of tasks: const tasks: Task[] = [...].\n"
            "   - Use useState to track selectedTaskId.\n"
            "   - Derive selectedTask from tasks + selectedTaskId.\n"
            "   - Render a responsive two-column layout using Tailwind.\n"
            "7. ABSOLUTELY NO:\n"
            "   - Markdown code fences like ```tsx or ```ts.\n"
            "   - Text such as 'Here is the code', 'Explanation', or similar.\n"
            "   - TODO markers or placeholder pseudo-code.\n"
        )

        # 2) USER PROMPT: spec + minimal direct request
        user_prompt = (
            "# Project Spec\n\n"
            f"{ctx.spec_text}\n\n"
            "# Task\n"
            f"Generate the COMPLETE contents of `{target_path}` as a single TSX/TS file, "
            "following ALL rules in the system message. "
            "Output ONLY the raw file contents."
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

        cleaned = self._strip_fence(code)
        ctx.generated_code = cleaned

    @staticmethod
    def _strip_fence(text: str) -> str:
        """
        Defensive cleanup in case the model still wraps the code in ``` fences.
        """
        stripped = text.strip()

        # Common case: ```tsx ... ``` or ```ts ... ```
        if stripped.startswith("```"):
            lines = stripped.splitlines()

            # Drop first line (``` or ```tsx/ts)
            if lines:
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
