````markdown
# AI-Orchestrated Workflow Project

This is a minimal template for creating new AI-powered workflow tools using a step-based orchestration engine and a local language model (LM Studio).

## Requirements
- Python 3.10+
- LM Studio running locally at `http://localhost:1234/v1`
- `pip install -r requirements.txt`

## Running the Example

```bash
python -m run_task
````

## Structure

* `orchestrator/` — Engine + Steps + Local LLM wrapper
* `tasks/` — Define workflow pipelines
* `examples/` — Input/output files
* `run_task.py` — Entrypoint

````
