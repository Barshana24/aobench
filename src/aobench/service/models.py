"""Thin transport-agnostic models returned by the service façade (spec-0001).

Where an existing schema already fits (BenchmarkResult, Trace) it is reused
directly; these models add only what the façade needs on top.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel

from aobench.schemas.result import BenchmarkResult


class Fingerprint(BaseModel):
    """Reproducibility fingerprint (ADR 0005) attached to every run."""

    env_manifest_sha256: Optional[str] = None
    model_snapshot: Optional[str] = None
    adapter: str
    scoring_profile_version: str = "default_hpc_v01"
    seed: Optional[int] = None
    replay: str = "live"


class RunHandle(BaseModel):
    """Returned by submit_run — a pointer to a run plus its terminal status.

    In the sync path status is 'completed'; in the async path (ADR 0002) it is
    'queued' with the same run_id shape.
    """

    run_id: str
    status: str  # queued | working | completed | failed
    aggregate_score: Optional[float] = None
    fingerprint: Optional[Fingerprint] = None


class RunRecord(BaseModel):
    """Full record of a run read back from disk."""

    run_id: str
    status: str
    n_tasks: int
    aggregate_score: Optional[float] = None  # mean across tasks
    hard_fail_count: int = 0
    results: list[BenchmarkResult] = []
    fingerprint: Optional[Fingerprint] = None


class TaskSummary(BaseModel):
    task_id: str
    qcat: Optional[str] = None
    role: Optional[str] = None
    environment_id: Optional[str] = None
    scoring_mode: Optional[str] = None
    difficulty_tier: Optional[int] = None


class EnvSummary(BaseModel):
    env_id: str
    manifest_sha256: Optional[str] = None
    n_files: Optional[int] = None


class CompareResult(BaseModel):
    run_a: str
    run_b: str
    aggregate_a: Optional[float] = None
    aggregate_b: Optional[float] = None
    delta: Optional[float] = None
    per_dimension_delta: dict[str, Optional[float]] = {}


class RobustnessResult(BaseModel):
    task_id: str
    env_id: str
    adapter: str
    n: int
    scores: list[Optional[float]] = []
    mean: Optional[float] = None
    stdev: Optional[float] = None
    run_ids: list[str] = []
    # Measurement rigor (Feature 27): pass^k + bootstrap CI over the n scores.
    pass_threshold: Optional[float] = None
    pass_1: Optional[float] = None
    pass_k: Optional[float] = None
    k: Optional[int] = None
    ci_low: Optional[float] = None
    ci_high: Optional[float] = None


class ReportModel(BaseModel):
    """Generic wrapper so transports get a typed object regardless of format."""

    run_id: str
    format: str
    payload: Any


class DatasetInfo(BaseModel):
    """A versioned task corpus and its splits (Feature 5)."""

    dataset_version: str
    frozen_date: Optional[str] = None
    n_tasks: int
    split_counts: dict[str, int] = {}
