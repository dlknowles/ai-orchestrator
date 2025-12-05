from __future__ import annotations
from pathlib import Path
from typing import List
from .context import CodegenContext
from .steps import (
    LoadProjectSpecStep,
    ProjectScanningStep,
    GenerateComponentStep,
    BackupExistingFileStep,
    WriteGeneratedFileStep,
    Step,
)


class CodegenTask:
    def __init__(
        self,
        project_path: Path,
        spec_path: Path,
        target_file: Path,
        steps: List[Step] | None = None,
    ) -> None:
        self.ctx = CodegenContext(
            project_path=project_path,
            spec_path=spec_path,
            target_file=target_file,
        )
        self.steps: List[Step] = steps or [
            LoadProjectSpecStep(),
            ProjectScanningStep(),
            GenerateComponentStep(),
            BackupExistingFileStep(),
            WriteGeneratedFileStep(),
        ]

    def run(self) -> None:
        for step in self.steps:
            step.run(self.ctx)
