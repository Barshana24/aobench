"""Statistical rigor utilities for AOBench (Feature 27).

pass^k reliability, bootstrap confidence intervals, and best-of-n — pure
functions with deterministic (seeded) resampling.
"""

from __future__ import annotations

from aobench.analysis.accounting import RunAccounting, account_run
from aobench.analysis.contamination import ContaminationReport, check_contamination, output_diversity
from aobench.analysis.rigor import (
    RigorSummary,
    bootstrap_ci,
    pass_hat_k,
    pass_k_from_scores,
    summarize_scores,
)

__all__ = [
    "pass_hat_k",
    "pass_k_from_scores",
    "bootstrap_ci",
    "summarize_scores",
    "RigorSummary",
    "account_run",
    "RunAccounting",
    "check_contamination",
    "output_diversity",
    "ContaminationReport",
]
