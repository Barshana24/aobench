"""Integration test: M100 tasks run end-to-end through the runner and produce a result."""

from __future__ import annotations

from pathlib import Path

import pytest

from aobench.adapters.direct_qa_adapter import DirectQAAdapter
from aobench.runners.runner import BenchmarkRunner
from aobench.schemas.result import BenchmarkResult

BENCHMARK_ROOT = Path(__file__).resolve().parents[2] / "benchmark"

_CASES = [
    ("M100_MON_SYS_001", "env_m100_01",
     "Node r3n7 GPU3 is overheating: gpu3_core_temp reached ~88C, crossing the throttle threshold."),
    ("M100_ENERGY_SYS_001", "env_m100_02",
     "Node r10n4 total_power spiked to ~1400W, ~117% over the ~644W rack baseline."),
    ("M100_ENERGY_FAC_002", "env_m100_03",
     "A rack-4 cooling fault: ambient rose to ~32C on all nodes; escalate to facilities."),
    ("M100_MON_SYS_002", "env_m100_04",
     "Node r7n2 is down: its telemetry stopped at ~10:45 UTC and SLURM marks it down."),
    ("M100_JOB_USR_001", "env_m100_05",
     "Job 7798450 on r2n5 FAILED at ~15:30 UTC; total_power collapsed to ~260W as the job died."),
    ("M100_JOB_USR_002", "env_m100_06",
     "Job 66353 on r5n3 was OOM-killed: mem_free fell to near-zero vs ~315GB total; reduce memory use."),
]


@pytest.mark.parametrize("task_id,env_id,answer", _CASES)
def test_m100_task_scores(tmp_path, task_id, env_id, answer):
    runner = BenchmarkRunner(
        adapter=DirectQAAdapter(answer=answer),
        benchmark_root=BENCHMARK_ROOT,
        output_root=tmp_path,
    )
    result = runner.run(task_id, env_id)

    assert isinstance(result, BenchmarkResult)
    assert result.task_id == task_id
    assert result.environment_id == env_id
    assert result.aggregate_score is not None
    assert 0.0 <= result.aggregate_score <= 1.0
    assert result.dimension_scores.outcome is not None
