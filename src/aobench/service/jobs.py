"""Job registry + lifecycle — pure core (Feature 2).

Long agent sweeps need to be decoupled from the request that starts them, with
status that survives a worker restart. The durable backend (arq + Redis, ADR
0002) is infra; this module is the persistence-agnostic **core**: a thread-safe
job registry and the state machine every backend must implement.

``run_job`` drives one job through ``queued → running → completed|failed`` around
a supplied callable, capturing the ``run_id``/score on success and the error on
failure. A synchronous caller, a background thread, or an arq worker can all use
it identically — only *where* the callable runs differs.
"""

from __future__ import annotations

import threading
from typing import Callable, Literal, Optional

from pydantic import BaseModel

JobState = Literal["queued", "running", "completed", "failed", "canceled"]

_TERMINAL: set[JobState] = {"completed", "failed", "canceled"}


class JobRecord(BaseModel):
    job_id: str
    state: JobState = "queued"
    task_id: str
    env_id: str
    adapter: str
    run_id: Optional[str] = None
    aggregate_score: Optional[float] = None
    error: Optional[str] = None
    seq: int = 0                       # monotonic submit order (deterministic, no clock)
    attempts: int = 0


class JobResult(BaseModel):
    """What a job's callable returns on success."""

    run_id: str
    aggregate_score: Optional[float] = None


class InMemoryJobRegistry:
    """Thread-safe in-memory job registry (reference backend).

    Mirrors the interface a Redis/arq-backed registry implements, so the façade
    and REST ``wait=false`` path can be written against it and swapped later.
    """

    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._lock = threading.Lock()
        self._counter = 0

    def submit(self, task_id: str, env_id: str, adapter: str, *, job_id: str) -> JobRecord:
        with self._lock:
            if job_id in self._jobs:
                raise ValueError(f"duplicate job_id {job_id!r}")
            self._counter += 1
            rec = JobRecord(job_id=job_id, task_id=task_id, env_id=env_id,
                            adapter=adapter, seq=self._counter)
            self._jobs[job_id] = rec
            return rec.model_copy(deep=True)

    def get(self, job_id: str) -> Optional[JobRecord]:
        with self._lock:
            rec = self._jobs.get(job_id)
            return rec.model_copy(deep=True) if rec else None

    def list(self, *, state: Optional[JobState] = None) -> list[JobRecord]:
        with self._lock:
            recs = sorted(self._jobs.values(), key=lambda r: r.seq)
            return [r.model_copy(deep=True) for r in recs if state is None or r.state == state]

    def _transition(self, job_id: str, **changes: object) -> JobRecord:
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                raise KeyError(job_id)
            updated = rec.model_copy(update=changes)
            self._jobs[job_id] = updated
            return updated.model_copy(deep=True)

    def mark_running(self, job_id: str) -> JobRecord:
        rec = self.get(job_id)
        if rec is None:
            raise KeyError(job_id)
        return self._transition(job_id, state="running", attempts=rec.attempts + 1)

    def mark_completed(self, job_id: str, run_id: str,
                       aggregate_score: Optional[float] = None) -> JobRecord:
        return self._transition(job_id, state="completed", run_id=run_id,
                                aggregate_score=aggregate_score)

    def mark_failed(self, job_id: str, error: str) -> JobRecord:
        return self._transition(job_id, state="failed", error=error)

    def cancel(self, job_id: str) -> JobRecord:
        rec = self.get(job_id)
        if rec is None:
            raise KeyError(job_id)
        if rec.state in _TERMINAL:
            return rec  # cannot cancel a finished job
        return self._transition(job_id, state="canceled")


def run_job(
    registry: InMemoryJobRegistry, job_id: str, fn: Callable[[], JobResult]
) -> JobRecord:
    """Drive one job through its lifecycle around ``fn``.

    Skips execution if the job was canceled before it started. On success records
    the run_id/score; on any exception records a failure (never re-raises) so the
    registry always reflects a terminal state a caller can poll.
    """
    current = registry.get(job_id)
    if current is None:
        raise KeyError(job_id)
    if current.state == "canceled":
        return current

    registry.mark_running(job_id)
    try:
        result = fn()
    except Exception as exc:  # noqa: BLE001 — surfaced via job state, not raised
        return registry.mark_failed(job_id, f"{type(exc).__name__}: {exc}")
    return registry.mark_completed(job_id, result.run_id, result.aggregate_score)
