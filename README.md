# AI Orchestrator (Local, Step-Based)

A minimal, reusable framework for building small AI-powered workflows using a step-based orchestration engine and a local language model served through LM Studio.

This is designed to be simple, fast to extend, and dependency-light — a starter kit for creating new AI-driven utilities and automations.

---

## Features

- **Step-based execution model** (Engine → Steps → Context)
- **Local LLM integration** via LM Studio (OpenAI-compatible API)
- **Simple file-based tasks** (load → transform → save)
- **Easily extendable** with custom Steps

No agents, no LangChain, no unnecessary complexity.

---

## Requirements

- **Python 3.10+** (this project was built on 3.14)
- **LM Studio** running locally  
  - Local server must be available at: `http://localhost:1234/v1`
  - Load any small instruct model (e.g., Qwen 2.5 3B, Phi-3 Mini, Mistral 7B)
- `pip install -r requirements.txt`

---

## Project Structure

```

ai-orchestrator/
│
├── orchestrator/
│   ├── engine.py          # Executes steps in sequence
│   ├── llm.py             # Wrapper around LM Studio's local API
│   └── steps/
│       ├── base.py        # Step interface + Context
│       ├── file_ops.py    # LoadFile, WriteFile
│       └── llm_step.py    # Generic LLM-powered step
│
├── tasks/
│   ├── example_task.py    # Simple demo workflow
│   └── readme_improver_task.py  # README improver example
│
├── examples/
│   ├── input.txt
│   └── output.txt
│
└── run_task.py            # Runs the selected task

````

---

## Running the Example

1. Start LM Studio  
   - Open LM Studio  
   - Load a small instruct model  
   - Go to **Server** → click **Start Local Server**
   - Confirm it is running at:  
     `http://localhost:1234/v1`

2. Run the orchestrator:

```bash
python -m run_task
````

This will:

* load `examples/input.txt`
* process it using the LLM
* write the result to `examples/output.txt`

---

## Creating a New LLM Task

Each workflow is defined as a sequence of Steps.

Minimal example:

```python
from orchestrator.engine import Engine
from orchestrator.steps.file_ops import LoadFile, WriteFile
from orchestrator.steps.llm_step import LLMStep

def build_my_engine() -> Engine:
    system_prompt = (
        "Rewrite the input text clearly and concisely. "
        "Do NOT invent details or add information."
    )

    steps = [
        LoadFile("input.txt", context_key="input_text"),
        LLMStep(system_prompt, "input_text", "output_text"),
        WriteFile("output.txt", "output_text"),
    ]

    return Engine(steps)
```

Then run it with a small runner:

```bash
python -m run_my_task
```

---

## Notes

* This project is meant to be extended into many small AI utilities.
* Keep steps small and composable.
* Favor simple workflows over complex agent logic.