---
title: "Evaluate your own agent with AOBench"
description: "Three ways to run your own AI agent through the AOBench HPC benchmark: point the MCP adapter at your server, point the OpenAI adapter at any compatible endpoint, or write a ~40-line custom adapter."
keywords:
  - evaluate my own agent
  - custom benchmark adapter
  - MCP agent evaluation
  - benchmark local LLM
---

# Evaluate your own agent

AOBench evaluates *systems*, not just models. Anything that can receive an operational
question and return an answer — optionally calling tools along the way — can be scored.
There are three routes, in increasing order of effort.

## Route 1 — your agent speaks MCP (no code)

If your agent is an MCP server, you are done:

```bash
aobench run all --adapter "mcp:stdio:python your_server.py" --split dev
```

AOBench spawns the server, offers it the role-filtered HPC tool set for each task,
records every call it makes, and scores the resulting trace. This is the recommended
route for anything you did not write yourself, and for anything you want other people
to be able to re-run.

## Route 2 — your agent speaks the OpenAI chat API (no code)

Any OpenAI-compatible endpoint works, including local servers such as vLLM, llama.cpp,
Ollama's compatibility layer, or your own gateway:

```bash
export OPENAI_BASE_URL=http://localhost:8000/v1
export OPENAI_API_KEY=not-needed-but-must-be-set
aobench run all --adapter openai:your-model-name --split dev
```

!!! tip "Pin the model snapshot"
    Use the dated snapshot (`gpt-4o-2024-11-20`) rather than the moving alias
    (`gpt-4o`). A provider silently updating an alias is the most common reason a
    re-run does not reproduce — see [versioning](../about/versioning.md).

## Route 3 — write an adapter (about 40 lines)

For a bespoke agent — a multi-agent system, a research prototype, something with its
own planner — implement one method.

### The interface

```python
from aobench.adapters.base import BaseAdapter
from aobench.schemas.trace import Trace

class MyAdapter(BaseAdapter):
    name = "my_agent"

    def run(self, context) -> Trace:
        ...
```

`context` is an `ExecutionContext` carrying everything your agent is allowed to see:

| Attribute | What it is |
|---|---|
| `context.task` | The `TaskSpec` — `query_text`, `role`, `qcat`, `allowed_tools` |
| `context.env` | The loaded `EnvironmentBundle` |
| `context.tools` | The role-filtered `ToolRegistry` — the only tools you may call |
| `context.run_id` | The run this task belongs to |

The registry exposes exactly two things you need:

```python
context.tools.available_tool_names          # -> ["slurm", "telemetry", "docs", ...]
context.tools.call(tool_name, method, **kwargs)   # -> ToolResult
```

**Only call tools through `context.tools`.** That registry is what enforces RBAC:
calling a tool outside your role returns a `ToolResult` with `permission_denied=True`
rather than raising, and that denial is what the governance dimension scores. Reading
the snapshot directly instead is how you accidentally build an agent that scores well
and would be an incident in production.

### A working skeleton

```python
from datetime import datetime, timezone

from aobench.adapters.base import BaseAdapter
from aobench.schemas.trace import Trace, TraceStep
from aobench.utils.ids import make_trace_id


class MyAdapter(BaseAdapter):
    """Minimal adapter: one tool call, then an answer."""

    name = "my_agent"

    def run(self, context) -> Trace:
        start = datetime.now(tz=timezone.utc)
        steps: list[TraceStep] = []

        # 1. Decide what to do. Your agent's logic goes here.
        question = context.task.query_text
        allowed = context.tools.available_tool_names

        # 2. Call a tool through the registry: (tool_name, method, **kwargs).
        #    RBAC is enforced here and the call lands in the scored trace.
        result = context.tools.call("slurm", "get_job_details", job_id="12345")

        steps.append(
            TraceStep(
                step_id=1,
                reasoning=f"Role {context.task.role} may use {allowed}; checking the job.",
                tool_call={"tool": "slurm", "method": "get_job_details",
                           "args": {"job_id": "12345"}},
                observation=result.model_dump() if hasattr(result, "model_dump") else result,
                timestamp=datetime.now(tz=timezone.utc),
            )
        )

        # 3. Produce the final answer.
        answer = my_agent_logic(question, result)

        return Trace(
            trace_id=make_trace_id(),
            run_id=context.run_id,
            task_id=context.task.task_id,
            role=context.task.role,
            environment_id=context.env.metadata.environment_id,
            adapter_name=self.name,
            steps=steps,
            final_answer=answer,
            start_time=start,
            end_time=datetime.now(tz=timezone.utc),
            total_tokens=0,
            hard_fail=False,
        )
```

For the exact `TraceStep` field shapes the shipped adapters use, read
[`openai_adapter.py`](https://github.com/MSKazemi/aobench/blob/main/src/aobench/adapters/openai_adapter.py)
around its tool-calling loop — it is the reference implementation.


### Register it

Add your adapter to the registry in `src/aobench/cli/run_cmd.py`, then:

```bash
aobench run task --task JOB_USR_001 --env env_01 --adapter my_agent
```

If your adapter is generally useful, **please contribute it** — a new adapter is one of
the highest-value contributions to this project, because it makes a whole class of
agent evaluable by everyone. See [contributing](../about/contributing.md).

## Interpreting your first results

Run the baseline alongside your agent, always:

```bash
aobench run all --adapter direct_qa --split dev
aobench run all --adapter my_agent  --split dev
aobench compare runs <baseline_run_id> <your_run_id>
```

| Symptom | Usually means |
|---|---|
| Score below `direct_qa` | Your agent calls tools badly — worse than not calling them |
| High outcome, low grounding | It is guessing right, not diagnosing |
| High outcome, governance hard-fails | The dangerous profile — competent until it oversteps |
| Good single-run, bad `pass^k` | Inconsistent; not an operator you would trust |
| Low tool_use, high outcome | It answers from parametric knowledge, not from the snapshot |

The last two are the ones people miss. Run
`aobench robustness task --task <id> --env <id> --adapter my_agent --n 5` before you
believe any single-shot number.

## Publishing your result

Report the version, split, profile, and adapter — see
[versioning](../about/versioning.md) — and consider
[submitting it to the leaderboard](../leaderboard.md).
