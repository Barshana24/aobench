#!/usr/bin/env python3
"""Example 2 — score a trace your own system produced.

The "bring your own agent" path. If your agent already runs somewhere else — a
notebook, a service, a different harness — you do not need to write an AOBench adapter
to get an AOBench score. Build a ``Trace``, hand it to ``AggregateScorer``, done.

    python examples/02_score_a_trace.py

This is also how to re-score an old run under a different weight profile without
re-running the agent, which is the cheap way to check whether a model ranking is
weight-invariant (see RESEARCH.md, R12).
"""

from __future__ import annotations

from datetime import datetime, timezone

from aobench.loaders.task_loader import load_task
from aobench.paths import resolve_benchmark_root
from aobench.schemas.trace import Observation, ToolCall, Trace, TraceStep
from aobench.scorers.aggregate import AggregateScorer
from aobench.utils.ids import make_run_id, make_trace_id

TASK_ID = "JOB_USR_001"


def build_trace(task) -> Trace:  # noqa: ANN001 - TaskSpec
    """Construct a Trace as if some external agent had produced it."""
    now = datetime.now(tz=timezone.utc)
    return Trace(
        trace_id=make_trace_id(),
        run_id=make_run_id(),
        task_id=task.task_id,
        role=task.role,
        environment_id=task.environment_id,
        adapter_name="external_system",
        steps=[
            TraceStep(
                step_id=1,
                step_type="tool_call",
                reasoning="Check the failed job before concluding anything.",
                tool_call=ToolCall(
                    tool_name="slurm",
                    method="get_job_details",
                    arguments={"job_id": "12345"},
                ),
                observation=Observation(
                    content={"job_id": "12345", "state": "OUT_OF_MEMORY"},
                ),
                timestamp=now,
            ),
        ],
        final_answer=(
            "Job 12345 was killed by the out-of-memory handler. Request more memory "
            "per task with --mem-per-cpu and resubmit."
        ),
        start_time=now,
        end_time=now,
        total_tokens=0,
        hard_fail=False,
    )


def main() -> int:
    root = resolve_benchmark_root("benchmark")
    task = load_task(root / "tasks" / "specs" / f"{TASK_ID}.json")
    trace = build_trace(task)

    profiles = root / "configs" / "scoring_profiles.yaml"
    scorer = AggregateScorer(profiles)
    result = scorer.score(task, trace, run_id=trace.run_id)

    print(f"Scored an externally-produced trace for {TASK_ID}\n")
    print(f"  aggregate : {result.aggregate_score:.4f}")
    print(f"  hard fail : {result.hard_fail}")
    print("\n  per dimension:")
    dims = result.dimension_scores
    for name in ("outcome", "tool_use", "grounding", "governance", "efficiency"):
        value = getattr(dims, name, None)
        if value is not None:
            print(f"    {name:<12} {float(value):.4f}")

    print(
        "\nNothing here required an adapter: any system that can emit a Trace can be "
        "scored by AOBench."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
