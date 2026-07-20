"""Tests for the A2A orchestrator/worker adapter pure core (Feature 12)."""

from __future__ import annotations

from types import SimpleNamespace

from aobench.a2a.adapter import (
    A2ADelegationEvent,
    A2AOrchestratorAdapter,
    build_multi_agent_trace,
)
from aobench.a2a.scorers import attribute_failure, delegation_quality
from aobench.a2a.schema import TaskState


def _ctx(task_id="JOB_USR_001"):
    return SimpleNamespace(task=SimpleNamespace(task_id=task_id))


def test_build_trace_shape_and_workers_order():
    events = [
        A2ADelegationEvent(subtask="diagnose", to_agent="w_diag", messages=2, tokens=100),
        A2ADelegationEvent(subtask="remediate", to_agent="w_ops", messages=1, tokens=50),
        A2ADelegationEvent(subtask="verify", to_agent="w_diag"),  # repeat worker
    ]
    tr = build_multi_agent_trace("T1", events)
    assert tr.task_id == "T1"
    assert tr.workers == ["w_diag", "w_ops"]         # first-seen order, deduped
    assert len(tr.delegations) == 3
    assert tr.total_messages() == 4
    assert tr.total_tokens() == 150
    assert tr.run_failed is False


def test_run_failed_inferred_from_failure_state():
    events = [A2ADelegationEvent(subtask="x", to_agent="w1", result_state=TaskState.FAILED)]
    tr = build_multi_agent_trace("T1", events)
    assert tr.run_failed is True


def test_run_failed_inferred_from_caused_failure():
    events = [A2ADelegationEvent(subtask="x", to_agent="w1", caused_failure=True)]
    tr = build_multi_agent_trace("T1", events)
    assert tr.run_failed is True


def test_feeds_delegation_quality_scorer():
    events = [
        A2ADelegationEvent(subtask="diagnose", to_agent="w_diag"),
        A2ADelegationEvent(subtask="remediate", to_agent="w_ops"),
    ]
    tr = build_multi_agent_trace(
        "T1", events, gold_delegation_map={"diagnose": "w_diag", "remediate": "w_ops"})
    r = delegation_quality(tr)
    assert r.score == 1.0
    assert r.correct == 2


def test_feeds_failure_attribution_scorer():
    events = [A2ADelegationEvent(subtask="x", to_agent="w_bad", caused_failure=True)]
    tr = build_multi_agent_trace("T1", events, gold_failure_agent="w_bad")
    r = attribute_failure(tr)
    assert r.run_failed is True
    assert r.predicted_agent == "w_bad"
    assert r.correct is True


def test_adapter_run_multi_agent():
    events = [A2ADelegationEvent(subtask="s", to_agent="w1")]
    adapter = A2AOrchestratorAdapter(
        delegation_source=lambda ctx: events,
        gold_delegation_map={"s": "w1"},
    )
    tr = adapter.run_multi_agent(_ctx())
    assert tr.task_id == "JOB_USR_001"
    assert tr.workers == ["w1"]
    assert delegation_quality(tr).score == 1.0


def test_empty_events():
    tr = build_multi_agent_trace("T1", [])
    assert tr.workers == []
    assert tr.run_failed is False
