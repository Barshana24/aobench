"""Contamination / memorization guard (Feature 26).

When a task is exposed publicly (e.g. via the REST API) it can leak into training
sets. Two cheap defenses:

- **Env fingerprint pinning** happens in the service façade (env.manifest_sha256).
- **Cross-session diversity probe** (here): solving the same task N times in
  isolated sessions at temperature > 0 should yield *diverse* outputs. Very low
  diversity is a memorization signal.

Plus a canary check: if a task embeds a canary string and it appears in model
output, that's direct evidence of training leakage.
"""

from __future__ import annotations

from pydantic import BaseModel


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def output_diversity(outputs: list[str]) -> float:
    """Fraction of distinct (normalized) outputs — 1.0 = all unique, →0 = identical."""
    non_empty = [o for o in outputs if o and o.strip()]
    if not non_empty:
        return 0.0
    distinct = {_normalize(o) for o in non_empty}
    return len(distinct) / len(non_empty)


class ContaminationReport(BaseModel):
    n_samples: int
    diversity: float
    likely_memorized: bool
    canary_leaked: bool = False
    notes: str = ""


def check_contamination(
    outputs: list[str],
    *,
    diversity_threshold: float = 0.34,
    canary: str | None = None,
) -> ContaminationReport:
    """Flag likely memorization from low cross-session output diversity + canary leak."""
    div = output_diversity(outputs)
    n = len([o for o in outputs if o and o.strip()])
    # With ≥3 temperature>0 samples, near-identical output is suspicious.
    likely = n >= 3 and div <= diversity_threshold

    canary_leaked = False
    if canary:
        cnorm = _normalize(canary)
        canary_leaked = any(cnorm in _normalize(o) for o in outputs)

    flag = likely or canary_leaked
    return ContaminationReport(
        n_samples=n, diversity=round(div, 4), likely_memorized=flag,
        canary_leaked=canary_leaked,
        notes=(
            (f"low diversity {div:.2f} ≤ {diversity_threshold}" if likely else "diversity ok")
            + ("; CANARY LEAKED (training contamination)" if canary_leaked else "")
        ),
    )
