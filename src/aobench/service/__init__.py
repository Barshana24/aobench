"""AOBench service façade — transport-agnostic run/score/report engine access.

See design/adr/0001-multi-surface-access-architecture.md and
design/vision/specs/spec-0001-service-facade.md.
"""

from __future__ import annotations

from aobench.service.errors import (
    AdapterError,
    AOBenchServiceError,
    EnvNotFound,
    RoleForbidden,
    RunNotFound,
    SplitLockedError,
    TaskNotFound,
)
from aobench.service.facade import BenchmarkService, resolve_adapter
from aobench.service.jobs import (
    InMemoryJobRegistry,
    JobRecord,
    JobResult,
    JobState,
    run_job,
)
from aobench.service.models import (
    CompareResult,
    DatasetInfo,
    EnvSummary,
    Fingerprint,
    ReportModel,
    RobustnessResult,
    RunHandle,
    RunRecord,
    TaskSummary,
)

__all__ = [
    "BenchmarkService",
    "resolve_adapter",
    "AOBenchServiceError",
    "TaskNotFound",
    "EnvNotFound",
    "AdapterError",
    "SplitLockedError",
    "RoleForbidden",
    "RunNotFound",
    "RunHandle",
    "RunRecord",
    "TaskSummary",
    "EnvSummary",
    "CompareResult",
    "RobustnessResult",
    "Fingerprint",
    "ReportModel",
    "DatasetInfo",
    "InMemoryJobRegistry",
    "JobRecord",
    "JobResult",
    "JobState",
    "run_job",
]
