"""Tests for the end-state verification scorer (Feature 21)."""

from __future__ import annotations

from aobench.cli_track.end_state import EndStateAssertion, score_end_state

STATE = {
    "jobs": {
        "123": {"qos": "normal", "partition": "gpu", "nodes": 4, "state": "PENDING"},
    },
    "files": ["submit.sh", "results.out"],
}


def test_all_pass():
    asserts = [
        EndStateAssertion(path="jobs.123.qos", op="equals", expected="normal"),
        EndStateAssertion(path="jobs.123.nodes", op="gte", expected=2),
    ]
    r = score_end_state(STATE, asserts)
    assert r.score == 1.0
    assert r.passed == 2


def test_partial():
    asserts = [
        EndStateAssertion(path="jobs.123.qos", op="equals", expected="normal"),   # pass
        EndStateAssertion(path="jobs.123.partition", op="equals", expected="cpu"),  # fail
    ]
    r = score_end_state(STATE, asserts)
    assert r.score == 0.5
    assert len(r.failures) == 1


def test_critical_failure_hard_fails():
    asserts = [
        EndStateAssertion(path="jobs.123.qos", op="equals", expected="high", critical=True),
    ]
    r = score_end_state(STATE, asserts)
    assert r.hard_fail is True
    assert r.score == 0.0
    assert r.hard_fail_reason is not None


def test_missing_path_fails():
    asserts = [EndStateAssertion(path="jobs.999.qos", op="exists")]
    r = score_end_state(STATE, asserts)
    assert r.passed == 0
    assert "<missing>" in r.failures[0]


def test_exists_op():
    asserts = [EndStateAssertion(path="jobs.123.state", op="exists")]
    assert score_end_state(STATE, asserts).score == 1.0


def test_in_set_and_contains():
    asserts = [
        EndStateAssertion(path="jobs.123.state", op="in_set", expected=["PENDING", "RUNNING"]),
        EndStateAssertion(path="files", op="contains", expected="results.out"),
    ]
    assert score_end_state(STATE, asserts).score == 1.0


def test_list_index_resolution():
    asserts = [EndStateAssertion(path="files.0", op="equals", expected="submit.sh")]
    assert score_end_state(STATE, asserts).score == 1.0


def test_weighted_assertions():
    asserts = [
        EndStateAssertion(path="jobs.123.qos", op="equals", expected="normal", weight=3.0),
        EndStateAssertion(path="jobs.123.partition", op="equals", expected="cpu", weight=1.0),
    ]
    r = score_end_state(STATE, asserts)
    assert r.score == 0.75  # 3/(3+1)


def test_no_assertions_is_1():
    assert score_end_state(STATE, []).score == 1.0
