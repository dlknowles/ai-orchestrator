from __future__ import annotations
from pathlib import Path
from typing import Protocol
import json
import os
import re
from .context import CodegenContext
from .llm_client import LMStudioClient


class Step(Protocol):
    def run(self, ctx: CodegenContext) -> None: ...


class LoadProjectSpecStep:
    def run(self, ctx: CodegenContext) -> None:
        ctx.ensure_project_exists()
        ctx.ensure_spec_exists()

        ctx.spec_text = ctx.spec_path.read_text(encoding="utf-8")

EXCLUDED_DIRS = {
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".next",
    ".turbo",
    ".cache",
}

EXCLUDED_FILE_NAMES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lockb",
}

MAX_FILES_IN_SUMMARY = 500  # safety cap for very large projects


class ProjectScanningStep:
    """
    Read-only structural scan of the project to give the LLM lightweight context:
    - directory and file list
    - file sizes

    Excludes heavy/noisy folders like node_modules and lockfiles.
    DOES NOT include file contents to keep the prompt well under context limits.
    """

    def run(self, ctx: CodegenContext) -> None:
        ctx.ensure_project_exists()
        root = ctx.project_path

        files_info: list[dict[str, object]] = []

        for dirpath, dirnames, filenames in os.walk(root):
            # filter out excluded dirs in-place so os.walk does not descend into them
            dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]

            for fname in filenames:
                if fname in EXCLUDED_FILE_NAMES:
                    continue

                fpath = Path(dirpath) / fname
                rel_path = fpath.relative_to(root).as_posix()

                # also exclude some obvious junk by suffix
                if rel_path.endswith(".log"):
                    continue

                try:
                    size_bytes = fpath.stat().st_size
                except OSError:
                    continue

                files_info.append(
                    {
                        "path": rel_path,
                        "size_bytes": size_bytes,
                    }
                )

                # safety cap to avoid giant monorepos blowing up the context
                if len(files_info) >= MAX_FILES_IN_SUMMARY:
                    break

            if len(files_info) >= MAX_FILES_IN_SUMMARY:
                break

        summary = {
            "root": str(root),
            "target_file": ctx.target_file.as_posix(),
            "files": files_info,
        }

        # Compact JSON: no spaces → fewer tokens
        ctx.project_context = json.dumps(summary, separators=(",", ":"))


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
            "4. Tailwind rules (STRICT):\n"
            "   - You may only use Tailwind classes that exist in the default Tailwind CSS config.\n"
            "   - DO NOT invent color shades such as bg-slate-750, text-slate-850, etc.\n"
            "   - Valid slate shades are ONLY: 50, 100, 200, 300, 400, 500, 600, 700, 800, 900.\n"
            "   - Use standard variants like hover:, focus:, active:, etc. Do NOT invent new variants.\n"
            "5. Functional + typed React:\n"
            "   - Use function components and hooks only (no class components).\n"
            "   - Define appropriate TypeScript types for props and data structures.\n"
            "6. Component composition and imports:\n"
            "   - You MUST obey any explicit component decomposition requirements in the spec.\n"
            "   - If the spec requires that this file import a component from a given relative path "
            "     (for example './components/Sidebar'), you MUST:\n"
            "       - Add a matching import statement at the top of the file.\n"
            "       - Use that imported component in the JSX.\n"
            "       - NOT define that component in this file.\n"
            "   - Do NOT ignore these requirements, even if the app could be implemented in a single component.\n"
            "7. Structure for this particular file (strongly preferred):\n"
            "   - Define Task and TaskStep types.\n"
            "   - Define a hard-coded array of tasks: const tasks: Task[] = [...].\n"
            "   - Use useState to track selectedTaskId.\n"
            "   - Derive selectedTask from tasks + selectedTaskId.\n"
            "   - Render a responsive two-column layout using Tailwind.\n"
            "8. ABSOLUTELY NO:\n"
            "   - Markdown code fences like ```tsx or ```ts.\n"
            "   - Text such as 'Here is the code', 'Explanation', or similar.\n"
            "   - TODO markers or placeholder pseudo-code.\n"
        )

        # 2) USER PROMPT: spec + minimal direct request
        project_context_section = ""
        if ctx.project_context:
            # Hard clamp to avoid context overflow in extreme cases
            MAX_CONTEXT_CHARS = 6000
            context_str = ctx.project_context
            if len(context_str) > MAX_CONTEXT_CHARS:
                context_str = context_str[:MAX_CONTEXT_CHARS] + ".../* project context trimmed by orchestrator */"
            project_context_section = "# Project Context (read-only)\n" + context_str + "\n\n"

        
        user_prompt = (
            project_context_section +
            "# Project Spec\n\n"
            f"{ctx.spec_text}\n\n"
            "# Task\n"
            f"Generate the COMPLETE contents of `{target_path}` as a single TSX/TS file, "
            "using the project context above when relevant and following ALL rules in the system message. "
            "Do NOT reference or modify any other files. "
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
        cleaned = self._sanitize_tailwind(cleaned)
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


    @staticmethod
    def _sanitize_tailwind(text: str) -> str:
        """
        Post-process Tailwind color classes to avoid invalid numeric shades, e.g. bg-slate-750
        or text-blue-845.

        For any color utility like:
          - bg-<color>-XYZ
          - text-<color>-XYZ
          - border-<color>-XYZ
          - outline-<color>-XYZ
          - ring-<color>-XYZ
          - from-<color>-XYZ
          - via-<color>-XYZ
          - to-<color>-XYZ
          - accent-<color>-XYZ
          - caret-<color>-XYZ
          - decoration-<color>-XYZ

        where XYZ is not a valid Tailwind shade, we:
        - Parse XYZ as an integer.
        - If 0–99    -> snap to 50.
        - If 100–199 -> snap to 100.
        - If 200–299 -> snap to 200.
        - ...
        - If 800–899 -> snap to 800.
        - If 900+    -> snap to 900.

        Non-color utilities (e.g. p-4, gap-2, z-50) are left untouched.
        """
        # Tailwind default color names
        color_names = (
            "slate", "gray", "zinc", "neutral", "stone",
            "red", "orange", "amber", "yellow",
            "lime", "green", "emerald", "teal", "cyan",
            "sky", "blue", "indigo", "violet", "purple",
            "fuchsia", "pink", "rose",
        )
        allowed_shades = {"50", "100", "200", "300", "400", "500", "600", "700", "800", "900"}

        # Build a regex that matches ONLY color utilities with numeric shades
        # e.g. bg-slate-750, text-blue-845, border-red-15, etc.
        color_names_pattern = "|".join(color_names)
        pattern = re.compile(
            rf"\b("
            rf"(?:bg|text|border|outline|ring|from|via|to|accent|caret|decoration)"
            rf"-(?:{color_names_pattern})-"
            rf")"
            rf"(\d{{1,3}})\b"
        )

        def snap_shade(shade_str: str) -> str:
            try:
                n = int(shade_str)
            except ValueError:
                # If it's not an int at all, just default to 700 as a safe fallback
                return "700"

            if n <= 99:
                return "50"
            if n >= 900:
                return "900"

            # 100–199 -> 100, 200–299 -> 200, etc.
            base = (n // 100) * 100
            # Clamp to valid range
            if base < 100:
                base = 100
            if base > 900:
                base = 900
            return str(base)

        def replace(match: re.Match) -> str:
            prefix, shade = match.group(1), match.group(2)
            if shade in allowed_shades:
                return match.group(0)

            snapped = snap_shade(shade)
            if snapped not in allowed_shades:
                # final safety: if somehow still not valid, default to 700
                snapped = "700"

            return f"{prefix}{snapped}"

        return pattern.sub(replace, text)


class BackupExistingFileStep:
    """
    If the target file already exists, create a timestamped backup copy
    under .orchestrator_backups/ relative to the project root.
    """

    def run(self, ctx: CodegenContext) -> None:
        abs_target = ctx.abs_target_file
        if not abs_target.is_file():
            # Nothing to back up
            return

        # .orchestrator_backups/src/App.tsx.20251205-132045.bak
        from datetime import datetime

        backup_root = ctx.project_path / ".orchestrator_backups"
        backup_root.mkdir(parents=True, exist_ok=True)

        rel_path = abs_target.relative_to(ctx.project_path)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        backup_dir = backup_root / rel_path.parent
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_file = backup_dir / f"{rel_path.name}.{timestamp}.bak"
        backup_file.write_text(abs_target.read_text(encoding="utf-8"), encoding="utf-8")


RELATIVE_IMPORT_PATTERN = re.compile(
    r"""import\s+(?:[^'"]+\s+from\s+)?['"](\./[^'"]*|\../[^'"]*)['"]""",
    re.MULTILINE,
)

DYNAMIC_IMPORT_PATTERN = re.compile(
    r"""import\(\s*['"](\./[^'"]*|\../[^'"]*)['"]\s*\)""",
    re.MULTILINE,
)


def _extract_relative_imports(source: str) -> list[str]:
    """
    Extract relative import specifiers from TS/TSX source code.

    Handles:
      import X from './foo';
      import { X } from '../bar/baz';
      import './side-effect';
      const mod = await import('./dynamic');
    """
    imports: set[str] = set()

    for m in RELATIVE_IMPORT_PATTERN.finditer(source):
        imports.add(m.group(1))

    for m in DYNAMIC_IMPORT_PATTERN.finditer(source):
        imports.add(m.group(1))

    return sorted(imports)


class ImportValidationStep:
    """
    Validates that all relative imports in the generated code point to existing files
    in the scanned project.

    Strict mode: if any import cannot be resolved to a real file, the step raises
    and the task fails. No file is written.
    """

    def __init__(self) -> None:
        # Extensions we consider when resolving bare import paths without an extension.
        self.candidate_exts: tuple[str, ...] = (
            ".tsx",
            ".ts",
            ".jsx",
            ".js",
            ".mjs",
            ".cjs",
            ".json",
        )

    def run(self, ctx: CodegenContext) -> None:
        if ctx.generated_code is None:
            raise ValueError("generated_code is not set. Run GenerateComponentStep first.")

        if not ctx.project_context:
            # If we somehow have no project context, we cannot validate; fail fast.
            raise ValueError("project_context is not set. Run ProjectScanningStep first.")

        try:
            context_obj = json.loads(ctx.project_context)
        except json.JSONDecodeError as exc:
            raise ValueError(f"project_context is not valid JSON: {exc}") from exc

        files = context_obj.get("files") or []
        existing_paths = {str(entry.get("path")) for entry in files if "path" in entry}

        # If project has no files, something is wrong; but don't block imports in that case.
        if not existing_paths:
            return

        # Extract relative imports from the generated source.
        imports = _extract_relative_imports(ctx.generated_code)
        if not imports:
            return  # nothing to validate

        base_dir = ctx.target_file.parent.as_posix()  # relative to project root

        missing: list[str] = []

        for spec in imports:
            # spec is something like './Foo' or '../components/Sidebar'
            # We resolve this relative to the target file directory.
            rel = Path(base_dir) / spec
            # Normalize to posix-style path relative to project root; remove leading './'
            rel_norm = rel.as_posix()
            if rel_norm.startswith("./"):
                rel_norm = rel_norm[2:]

            # If the spec already has an extension, check it directly.
            suffix = Path(rel_norm).suffix
            candidate_paths: list[str] = []

            if suffix:
                candidate_paths.append(rel_norm)
            else:
                # Try with our candidate extensions.
                stem_path = rel_norm
                candidate_paths.extend(stem_path + ext for ext in self.candidate_exts)
                # Also support index files in directories: ./foo -> ./foo/index.tsx, etc.
                candidate_paths.extend(
                    stem_path.rstrip("/") + "/index" + ext for ext in self.candidate_exts
                )

            # See if any candidate exists in the project file list.
            if not any(c in existing_paths for c in candidate_paths):
                missing.append(spec)

        if missing:
            details = "\n  ".join(missing)
            raise ValueError(
                "ImportValidationStep failed: the following relative imports do not "
                "resolve to existing files in the project:\n"
                f"  {details}\n\n"
                "Either adjust the spec/prompt, create the referenced files, or relax "
                "validation logic if this is intentional."
            )


class WriteGeneratedFileStep:
    def run(self, ctx: CodegenContext) -> None:
        if ctx.generated_code is None:
            raise ValueError("generated_code is not set. Run GenerateComponentStep first.")

        abs_target = ctx.abs_target_file
        abs_target.parent.mkdir(parents=True, exist_ok=True)
        abs_target.write_text(ctx.generated_code, encoding="utf-8")
        # MVP: direct overwrite. No diff/merge.
