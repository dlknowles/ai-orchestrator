# AI Orchestrator

AI Orchestrator is a modular, step-based automation engine designed to run structured tasks using local LLMs.  
It provides a framework for building code generation tools, automation agents, documentation writers, and general-purpose AI workflows that operate entirely on local resources through LM Studio.

This project is intended as both a fully working tool and a demonstration of how to build reliable, deterministic AI-driven development pipelines.

---

## Overview

The orchestrator is built around a simple architectural idea:

1. A **Task** defines a goal.
2. A task executes a sequence of **Steps**.
3. Each step receives and mutates a shared **Context**.
4. Steps are small, deterministic, and composable.
5. LM Studio provides local model inference through an OpenAI-compatible API.

This makes it easy to construct tasks for:
- Code generation  
- Code explanation  
- Documentation creation  
- Multi-step project automation  

---

## Features

### Step-Based Execution Pipeline
Tasks are defined as ordered sequences of steps. Each step performs one small, focused responsibility such as loading input data, analyzing a project, generating text with an LLM, or writing files to disk.

### Local-Only LLM Integration
All AI inference is performed through LM Studio running locally.  
No external API keys, network requirements, or usage costs.

### Project Specification Loading
The orchestrator can read specification files (such as `spec.md`) and pass them into the LLM as structured generation instructions.

### Lightweight Project Awareness
The system can scan a project directory and gather contextual information such as:
- Directory tree and file paths
- File sizes
- Exclusion of folders like node_modules, dist, .git
- Exclusion of package lock files

This context is provided to the LLM to improve determinism and reduce hallucinated imports or file references.

### Deterministic Code Generation
The `run_codegen` workflow uses:
- Strict system prompting
- Deterministic temperature settings
- Code-only output rules
- Removal of Markdown fences
- Tailwind class validation and sanitization
- Backup of pre-existing files before overwriting

The result is a stable, reliable single-file codegen pipeline suitable as a foundation for future multi-file generation.

### Automatic File Backup
Before writing any generated file, the orchestrator creates timestamped backups under `.orchestrator_backups/`.

### Post-Generation Tailwind Validation and Sanitization
The system corrects invalid Tailwind color classes by snapping non-existing shades to the nearest valid default Tailwind shade (50–900).  
Supports all Tailwind default color families.

---

## Included Tasks

The repository includes four runnable tasks, each demonstrating the orchestration engine in action.

### 1. Code Generation Task  
```bash
python -m run_codegen \
  --project-path "path/to/project" \
  --spec-path "path/to/spec.md" \
  --target-file "src/App.tsx"
````

Performs the full pipeline:

* Load specification
* Scan project structure
* Generate deterministic TypeScript/React code through LM Studio
* Validate and sanitize Tailwind classes
* Back up the original file
* Write the new file to disk

### 2. Code Explainer Task

```bash
python -m run_code_explainer \
  --file-path "path/to/file"
```

Reads a source file, sends it to the LLM with an explainer prompt, and returns a structured summary describing:

* What the code does
* Key functions or components
* Architectural roles
* Potential improvements or issues

Used as a basis for AI-assisted code review tooling.

### 3. README Generation Task

```bash
python -m run_readme_task \
  --project-path "path/to/project"
```

Scans the target project and generates a README.md based on:

* Project structure
* Code organization
* Configuration files
* Author instructions
* Intended usage patterns

This provides a repeatable method to create or regenerate project documentation.

### 4. Generic Task Runner

```bash
python -m run_task
```

Runs a generic example task using the base orchestrator pipeline.
Useful for testing new steps, debugging prompt construction, or building new workflows.

---

## Project Structure

```
ai-orchestrator/
│
├── orchestrator/
│   ├── codegen/
│   │   ├── context.py
│   │   ├── llm_client.py
│   │   ├── steps.py
│   │   ├── task.py
│   │
│   ├── explainer/
│   │   ├── steps.py
│   │   ├── task.py
│   │
│   ├── readme/
│   │   ├── steps.py
│   │   ├── task.py
│   │
│   ├── core/
│   │   ├── base_context.py
│   │   ├── base_step.py
│   │   ├── base_task.py
│
├── run_codegen.py
├── run_code_explainer.py
├── run_readme_task.py
├── run_task.py
└── README.md
```

---

## Requirements

* Python 3.10 or later
* LM Studio running locally on `http://localhost:1234/v1`
* Python dependencies (install using):

```bash
pip install -r requirements.txt
```

---

## Usage Summary

### Code Generation

Produces deterministic TypeScript/React files based on a markdown specification.

### Code Explanation

Summarizes and analyzes a source file.

### README Generation

Creates or regenerates a README for a target project based on its file structure and content.

### Custom Tasks

New tasks can be created by composing steps and implementing the desired pipeline behavior.

---

## License

MIT License