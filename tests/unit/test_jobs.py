"""Tests for the job registry + lifecycle pure core (Feature 2)."""

from __future__ import annotations

import pytest

from aobench.service.jobs import InMemoryJobRegistry, JobResult, run_job


@pytest.fixture()
def reg():
    return InMemoryJobRegistry()


def test_submit_and_get(reg):
    reg.submit("T1", "env_01", "direct_qa", job_id="j1")
    rec = reg.get("j1")
    assert rec.state == "queued"
    assert rec.task_id == "T1" and rec.seq == 1


def test_duplicate_job_id_rejected(reg):
    reg.submit("T1", "env_01", "direct_qa", job_id="j1")
    with pytest.raises(ValueError):
        reg.submit("T2", "env_01", "direct_qa", job_id="j1")


def test_list_order_and_filter(reg):
    reg.submit("T1", "env_01", "direct_qa", job_id="j1")
    reg.submit("T2", "env_01", "direct_qa", job_id="j2")
    reg.mark_running("j2")
    reg.mark_completed("j2", run_id="r2", aggregate_score=0.9)
    assert [r.job_id for r in reg.list()] == ["j1", "j2"]        # seq order
    assert [r.job_id for r in reg.list(state="completed")] == ["j2"]
    assert [r.job_id for r in reg.list(state="queued")] == ["j1"]


def test_lifecycle_completed(reg):
    reg.submit("T1", "env_01", "direct_qa", job_id="j1")
    ran = run_job(reg, "j1", lambda: JobResult(run_id="run-1", aggregate_score=0.83))
    assert ran.state == "completed"
    assert ran.run_id == "run-1" and ran.aggregate_score == 0.83
    assert reg.get("j1").attempts == 1


def test_lifecycle_failure_captured_not_raised(reg):
    reg.submit("T1", "env_01", "direct_qa", job_id="j1")

    def boom() -> JobResult:
        raise RuntimeError("adapter exploded")

    ran = run_job(reg, "j1", boom)          # must not raise
    assert ran.state == "failed"
    assert "adapter exploded" in ran.error


def test_cancel_before_run_skips_execution(reg):
    reg.submit("T1", "env_01", "direct_qa", job_id="j1")
    reg.cancel("j1")
    called = {"n": 0}

    def fn() -> JobResult:
        called["n"] += 1
        return JobResult(run_id="x")

    ran = run_job(reg, "j1", fn)
    assert ran.state == "canceled"
    assert called["n"] == 0                 # never executed


def test_cancel_terminal_job_is_noop(reg):
    reg.submit("T1", "env_01", "direct_qa", job_id="j1")
    run_job(reg, "j1", lambda: JobResult(run_id="r"))
    assert reg.cancel("j1").state == "completed"   # cannot cancel a finished job


def test_run_unknown_job_raises(reg):
    with pytest.raises(KeyError):
        run_job(reg, "nope", lambda: JobResult(run_id="r"))


def test_get_missing_returns_none(reg):
    assert reg.get("nope") is None
