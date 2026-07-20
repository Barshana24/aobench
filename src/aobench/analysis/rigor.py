"""pass^k reliability + bootstrap confidence intervals (Feature 27).

`pass^k` (τ-bench): the probability that *all* of k i.i.d. trials succeed —
the worst-case-consistency metric that matters for autonomous HPC operations,
where an occasionally-wrong action is unacceptable. We use the unbiased
combinatorial estimator over n observed trials with c successes:

    pass^k = C(c, k) / C(n, k)      (0 when c < k)

Bootstrap CIs use seeded resampling so a re-run reproduces the interval exactly
(ADR 0005 reproducibility).
"""

from __future__ import annotations

import random
from math import comb
from typing import Optional, Sequence

from pydantic import BaseModel


def pass_hat_k(n: int, c: int, k: int) -> float:
    """Unbiased estimate of pass^k given ``c`` successes out of ``n`` trials.

    Returns the probability that a random size-k subset of the n trials is
    all-success. Requires ``1 <= k <= n``; raises ValueError otherwise.
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    if n < k:
        raise ValueError(f"need at least k={k} trials, got n={n}")
    if c < k:
        return 0.0
    return comb(c, k) / comb(n, k)


def pass_k_from_scores(scores: Sequence[float], threshold: float, k: int) -> float:
    """pass^k where a trial 'succeeds' when its score >= ``threshold``."""
    vals = [s for s in scores if s is not None]
    n = len(vals)
    c = sum(1 for s in vals if s >= threshold)
    return pass_hat_k(n, c, k)


def bootstrap_ci(
    values: Sequence[float],
    confidence: float = 0.95,
    n_resamples: int = 2000,
    seed: int = 12345,
) -> tuple[float, float]:
    """Percentile bootstrap CI for the mean of ``values`` (deterministic via seed).

    Returns (low, high). For a single value returns (v, v); empty → (nan, nan).
    """
    vals = [float(s) for s in values if s is not None]
    if not vals:
        return (float("nan"), float("nan"))
    if len(vals) == 1:
        return (vals[0], vals[0])

    rng = random.Random(seed)
    n = len(vals)
    means: list[float] = []
    for _ in range(n_resamples):
        sample = [vals[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    alpha = (1.0 - confidence) / 2.0
    lo_idx = max(0, int(alpha * n_resamples))
    hi_idx = min(n_resamples - 1, int((1.0 - alpha) * n_resamples))
    return (means[lo_idx], means[hi_idx])


class RigorSummary(BaseModel):
    n: int
    mean: Optional[float] = None
    stdev: Optional[float] = None
    pass_threshold: float
    successes: int
    pass_1: Optional[float] = None   # fraction of trials that passed (pass@1)
    pass_k: Optional[float] = None   # all-k-succeed estimate
    k: int
    ci_low: Optional[float] = None
    ci_high: Optional[float] = None
    confidence: float = 0.95


def summarize_scores(
    scores: Sequence[float],
    *,
    threshold: float = 0.5,
    k: int = 2,
    confidence: float = 0.95,
    seed: int = 12345,
) -> RigorSummary:
    """Compute mean/stdev, pass@1, pass^k, and a bootstrap CI over ``scores``."""
    import statistics

    vals = [float(s) for s in scores if s is not None]
    n = len(vals)
    successes = sum(1 for s in vals if s >= threshold)
    mean = statistics.fmean(vals) if vals else None
    stdev = statistics.pstdev(vals) if len(vals) > 1 else (0.0 if vals else None)
    pass_1 = (successes / n) if n else None
    pk: Optional[float] = None
    if n >= k:
        pk = pass_hat_k(n, successes, k)
    ci_low, ci_high = (None, None)
    if vals:
        lo, hi = bootstrap_ci(vals, confidence=confidence, seed=seed)
        ci_low, ci_high = lo, hi

    return RigorSummary(
        n=n, mean=mean, stdev=stdev, pass_threshold=threshold, successes=successes,
        pass_1=pass_1, pass_k=pk, k=k, ci_low=ci_low, ci_high=ci_high, confidence=confidence,
    )
