"""Pure MCP handler logic — no FastMCP dependency.

Each function wraps the shared BenchmarkService façade and returns JSON-native
values (dicts for tools, JSON strings for resources). Keeping them free of
FastMCP makes them unit-testable without the optional extra; ``server.py`` binds
them to FastMCP tools/resources.
"""

from __future__ import annotations

import json
from typing import Any

from aobench.schemas.trace import Trace
from aobench.service import BenchmarkService

# ---------------------------------------------------------------------------
# Tools (side effects)
# ---------------------------------------------------------------------------

def run_task(
    svc: BenchmarkService,
    task_id: str,
    env_id: str,
    adapter: str = "direct_qa",
    role: str | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    """Execute one AOBench task against an environment snapshot.

    Returns the run_id, terminal status, aggregate score, and reproducibility
    fingerprint. Use ``get_report`` (resource) afterwards for the full scorecard.
    """
    handle = svc.submit_run(task_id, env_id, adapter, role=role, seed=seed, split="dev")
    return handle.model_dump(mode="json")


def score_trace(svc: BenchmarkService, task_id: str, trace: dict[str, Any]) -> dict[str, Any]:
    """Score a previously-captured trace against a task without re-running the agent."""
    parsed = Trace.model_validate(trace)
    return svc.score_trace(task_id, parsed).model_dump(mode="json")


def validate_benchmark(svc: BenchmarkService) -> dict[str, Any]:
    """Return counts of loadable tasks and environments (a lightweight health check)."""
    tasks = svc.list_tasks()
    envs = svc.list_envs()
    return {"n_tasks": len(tasks), "n_envs": len(envs), "ok": bool(tasks and envs)}


def robustness(
    svc: BenchmarkService, task_id: str, env_id: str, adapter: str = "direct_qa", n: int = 5
) -> dict[str, Any]:
    """Run a task ``n`` times and return score mean/stdev (consistency check)."""
    return svc.robustness(task_id, env_id, adapter, n).model_dump(mode="json")


# ---------------------------------------------------------------------------
# Resources (read-only) — return JSON strings
# ---------------------------------------------------------------------------

def catalog_tasks(svc: BenchmarkService) -> str:
    tasks = svc.list_tasks()
    return json.dumps({"count": len(tasks), "tasks": [t.model_dump() for t in tasks]})


def catalog_task(svc: BenchmarkService, task_id: str) -> str:
    for t in svc.list_tasks():
        if t.task_id == task_id:
            return json.dumps(t.model_dump())
    return json.dumps({"error": "task_not_found", "task_id": task_id})


def catalog_envs(svc: BenchmarkService) -> str:
    envs = svc.list_envs()
    return json.dumps({"count": len(envs), "envs": [e.model_dump() for e in envs]})


def run_report(svc: BenchmarkService, run_id: str) -> str:
    return json.dumps(svc.get_report(run_id, fmt="json").model_dump(), default=str)


def run_trace(svc: BenchmarkService, run_id: str) -> str:
    return svc.get_trace(run_id).model_dump_json()
