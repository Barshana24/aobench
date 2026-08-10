#!/usr/bin/env python3
"""Example 3 — write an adapter for your own agent.

This is the complete integration surface: one class, one method. The "agent" here is a
deliberately simple rule-based one so the example stays readable and runs offline, but
the structure is identical for an LLM, a multi-agent system, or a research prototype.

    python examples/03_custom_adapter.py

The one rule that matters: **call tools only through ``context.tools``**. That registry
is what enforces RBAC. Reading the snapshot directly would produce an agent that scores
well here and would be an incident on a real machine.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from aobench.adapters.base import BaseAdapter
from aobench.paths import resolve_benchmark_root
from aobench.runners.runner import BenchmarkRunner
from aobench.schemas.trace import Observation, ToolCall, Trace, TraceStep
from aobench.utils.ids import make_trace_id


class KeywordAdapter(BaseAdapter):
    """A rule-based 'agent': pick a tool by keyword, call it, report what it saw.

    Not a good agent. It is here to show the shape of an adapter, and — usefully — it
    demonstrates that calling tools at all already beats the tool-free baseline on some
    tasks, which is the first thing you want to confirm about your own integration.
    """

    name = "keyword_demo"

    #: Crude intent routing. A real adapter asks a model instead.
    _ROUTES: list[tuple[tuple[str, ...], str, str]] = [
        (("job", "failed", "queue", "submit"), "slurm", "get_job_details"),
        (("temperature", "power", "energy", "telemetry"), "telemetry", "get_summary"),
        (("policy", "documentation", "guide", "runbook"), "docs", "search"),
    ]

    def run(self, context) -> Trace:  # noqa: ANN001 - ExecutionContext, kept untyped for brevity
        start = datetime.now(tz=timezone.utc)
        question = (context.task.query_text or "").lower()
        allowed = context.tools.available_tool_names

        # 1. Decide which tool to reach for.
        tool_name, method = "slurm", "get_job_details"
        for keywords, candidate_tool, candidate_method in self._ROUTES:
            if any(word in question for word in keywords) and candidate_tool in allowed:
                tool_name, method = candidate_tool, candidate_method
                break

        # 2. Call it through the registry. A tool outside this role's permissions comes
        #    back as a ToolResult with permission_denied=True rather than raising — and
        #    that denial is exactly what the governance dimension scores.
        result = context.tools.call(tool_name, method)

        steps = [
            TraceStep(
                step_id=1,
                step_type="tool_call",
                reasoning=(
                    f"Role '{context.task.role}' may use {allowed}. "
                    f"Question mentions terms routed to '{tool_name}.{method}'."
                ),
                tool_call=ToolCall(tool_name=tool_name, method=method, arguments={}),
                observation=Observation(
                    content=result.data if hasattr(result, "data") else str(result),
                    error=getattr(result, "error", None),
                    permission_denied=getattr(result, "permission_denied", False),
                ),
                timestamp=datetime.now(tz=timezone.utc),
            )
        ]

        # 3. Answer. A real adapter synthesises this from the observation.
        answer = f"Consulted {tool_name}.{method}. Observation: {str(result)[:400]}"

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


def main() -> int:
    root = resolve_benchmark_root("benchmark")
    runner = BenchmarkRunner(
        adapter=KeywordAdapter(),
        benchmark_root=root,
        output_root=Path("data/runs"),
    )
    result = runner.run("JOB_USR_001", "env_01")

    print(f"adapter          : {KeywordAdapter.name}")
    print(f"aggregate score  : {result.aggregate_score:.4f}")
    print(f"hard fail        : {result.hard_fail}")
    print(
        "\nCompare against the tool-free baseline (examples/01_hello_aobench.py). "
        "If your adapter does not beat it, it is not using tools usefully yet."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
