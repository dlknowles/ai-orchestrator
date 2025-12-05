from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class CodegenContext:
    project_path: Path
    spec_path: Path
    target_file: Path  # relative to project_path, e.g. Path("src/App.tsx")

    spec_text: Optional[str] = None
    generated_code: Optional[str] = None

    @property
    def abs_target_file(self) -> Path:
        return self.project_path / self.target_file

    def ensure_project_exists(self) -> None:
        if not self.project_path.is_dir():
            raise FileNotFoundError(f"Project path does not exist: {self.project_path}")

    def ensure_spec_exists(self) -> None:
        if not self.spec_path.is_file():
            raise FileNotFoundError(f"Spec path does not exist: {self.spec_path}")
