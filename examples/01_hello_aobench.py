#!/usr/bin/env python3
"""Example 1 — run one AOBench task from Python, without the CLI.

The CLI is a thin wrapper over the same objects you can drive yourself. This is the
starting point for anyone embedding AOBench in a larger evaluation harness.

Runs offline, no API key:

    python examples/01_hello_aobench.py
"""

from __future__ import annotations

from pathlib import Path

from aobench.adapters.direct_qa_adapter import DirectQAAdapter
from aobench.paths import resolve_benchmark_root
from aobench.runners.runner import BenchmarkRunner

TASK_ID = "JOB_USR_001"
ENV_ID = "env_01"


def main() -> int:
    # 1. Find the corpus. Works from a source checkout or an installed wheel.
    root = resolve_benchmark_root("benchmark")
    print(f"Corpus: {root}")

    # 2. Pick an agent. DirectQAAdapter is the tool-free reference baseline —
    #    swap in your own adapter here and nothing else changes.
    adapter = DirectQAAdapter()

    # 3. Run one task against one environment.
    runner = BenchmarkRunner(
        adapter=adapter,
        benchmark_root=root,
        output_root=Path("data/runs"),
    )
    result = runner.run(TASK_ID, ENV_ID)

    # 4. Read the result.
    print(f"\nTask {TASK_ID} on {ENV_ID} with adapter '{adapter.name}'")
    print(f"  aggregate score : {result.aggregate_score:.4f}")
    print(f"  hard fail       : {result.hard_fail}")

    print("\n  per dimension:")
    dims = result.dimension_scores
    for name in ("outcome", "tool_use", "grounding", "governance", "efficiency"):
        value = getattr(dims, name, None)
        if value is not None:
            print(f"    {name:<12} {float(value):.4f}")

    print(
        "\nA low score is correct here: direct_qa calls no tools, so this is the floor "
        "a real agent has to beat — not a target."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
