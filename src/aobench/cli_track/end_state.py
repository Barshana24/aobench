"""End-state verification scorer (Feature 21).

Harbor-style grading: judge the **final environment state** (the sbatch directives
that landed, the QOS a job ended up in, a file that should exist) rather than the
agent's transcript. Judging outcomes instead of narration resists reward-hacking —
an agent can't earn credit by *claiming* success in prose.

Pure/deterministic: a harness snapshots the post-run state into a dict (e.g. from
the mock ``slurm_state.json`` after the agent's commands) and supplies the expected
assertions from the task's gold. A failed **critical** assertion (e.g. job in the
wrong QOS) is a hard-fail that zeroes the score.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel

_MISSING = object()


class EndStateAssertion(BaseModel):
    path: str                       # dot-path into the final-state dict, e.g. "jobs.123.qos"
    op: str = "equals"              # equals|not_equals|in_set|contains|gte|lte|exists
    expected: Any = None
    critical: bool = False          # failing this zeroes the whole score (hard-fail)
    weight: float = 1.0


class EndStateScore(BaseModel):
    score: float
    passed: int
    total: int
    hard_fail: bool = False
    hard_fail_reason: Optional[str] = None
    failures: list[str] = []
    notes: str = ""


def _resolve(state: dict[str, Any], path: str) -> Any:
    cur: Any = state
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError):
                return _MISSING
        else:
            return _MISSING
    return cur


def _check(op: str, actual: Any, expected: Any) -> bool:
    if op == "exists":
        return actual is not _MISSING
    if actual is _MISSING:
        return False
    if op == "equals":
        return bool(actual == expected)
    if op == "not_equals":
        return bool(actual != expected)
    if op == "in_set":
        return actual in (expected or [])
    if op == "contains":
        try:
            return expected in actual
        except TypeError:
            return False
    if op == "gte":
        try:
            return float(actual) >= float(expected)
        except (TypeError, ValueError):
            return False
    if op == "lte":
        try:
            return float(actual) <= float(expected)
        except (TypeError, ValueError):
            return False
    raise ValueError(f"unknown op: {op!r}")


def score_end_state(
    final_state: dict[str, Any], assertions: list[EndStateAssertion]
) -> EndStateScore:
    """Score the post-run environment state against expected assertions."""
    if not assertions:
        return EndStateScore(score=1.0, passed=0, total=0, notes="no assertions")

    passed = 0
    weight_hit = 0.0
    weight_total = 0.0
    failures: list[str] = []
    hard_fail = False
    hard_fail_reason: Optional[str] = None

    for a in assertions:
        actual = _resolve(final_state, a.path)
        ok = _check(a.op, actual, a.expected)
        weight_total += a.weight
        if ok:
            passed += 1
            weight_hit += a.weight
        else:
            shown = "<missing>" if actual is _MISSING else repr(actual)
            failures.append(f"{a.path} {a.op} {a.expected!r} (got {shown})")
            if a.critical:
                hard_fail = True
                hard_fail_reason = f"critical assertion failed: {a.path} {a.op} {a.expected!r}"

    if hard_fail:
        score = 0.0
    else:
        score = round(weight_hit / weight_total, 4) if weight_total else 1.0

    return EndStateScore(
        score=score, passed=passed, total=len(assertions),
        hard_fail=hard_fail, hard_fail_reason=hard_fail_reason, failures=failures,
        notes=f"{passed}/{len(assertions)} assertions passed",
    )
