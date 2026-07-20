"""Compute 95% Wilson CI on governance finding for paper.

E1 canonical results (dev split, n=58 tasks per model):
  GPT-4o:      governance = 0.216, outcome = 0.399
  GPT-4o-mini: governance = 0.138, outcome = 0.440
  Direct QA:   governance = 1.000, outcome = 0.276

The governance score is the mean across tasks; hard-fail rate is the fraction
with governance_score == 0.0 (RBAC violation). The binomial CI is computed on
the RBAC compliance rate (governance_score == 1.0 proportion).

Usage:
    uv run python scripts/compute_governance_ci.py
"""

from __future__ import annotations

from math import sqrt


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for proportion k/n."""
    if n == 0:
        return 0.0, 0.0
    p_hat = k / n
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    margin = z * sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


# E1 canonical results (project_exabench_results.md, v0.2.0 post-fix)
RESULTS = [
    {
        "model": "GPT-4o",
        "n": 58,
        "governance_mean": 0.216,
        # Treating governance_mean as RBAC compliance rate (fraction with gov=1.0)
        # 0.216 * 58 ≈ 12.5 → 13 compliant tasks; 78% failure rate (n_fail ≈ 45)
        "n_compliant": round(0.216 * 58),
        "hard_fail_rate": 0.78,
    },
    {
        "model": "GPT-4o-mini",
        "n": 58,
        "governance_mean": 0.138,
        "n_compliant": round(0.138 * 58),
        "hard_fail_rate": 0.862,
    },
    {
        "model": "GPT-4o-mini + RBAC prefix (E6)",
        "n": 58,
        "governance_mean": 0.276,
        "n_compliant": round(0.276 * 58),
        "hard_fail_rate": 0.724,
    },
]

print("95% Wilson confidence intervals on RBAC governance compliance rate")
print("(E1 canonical results, dev split, n=58 tasks per model)")
print()
print(f"{'Model':<40} {'n_compliant':>12} {'n':>4} {'Mean':>7} {'CI 95%':>20}  {'Failure rate':>14}")
print("-" * 105)

for r in RESULTS:
    k = r["n_compliant"]
    n = r["n"]
    lo, hi = wilson_ci(k, n)
    print(
        f"{r['model']:<40} {k:>12} {n:>4} {r['governance_mean']:>7.3f}"
        f" [{lo:.3f}, {hi:.3f}]{'':<6} {r['hard_fail_rate']:>12.1%}"
    )

print()
print("Paper text snippet (governance finding with CI):")
k_gpt4o = RESULTS[0]["n_compliant"]
n_gpt4o = RESULTS[0]["n"]
lo, hi = wilson_ci(k_gpt4o, n_gpt4o)
print(
    f"  GPT-4o achieved a governance score of {RESULTS[0]['governance_mean']:.3f} "
    f"(95% CI: [{lo:.3f}, {hi:.3f}], n={n_gpt4o}), "
    f"corresponding to a {RESULTS[0]['hard_fail_rate']:.0%} RBAC failure rate on dev-split tasks."
)
print()
print("E6 tradeoff (paper text):")
gov_base = RESULTS[1]["governance_mean"]
gov_rbac = RESULTS[2]["governance_mean"]
out_base = 0.440
out_rbac = 0.392
print(
    f"  Adding an RBAC-aware system prompt prefix improved governance from "
    f"{gov_base:.3f} to {gov_rbac:.3f} (+{(gov_rbac/gov_base - 1):.0%}), "
    f"at a cost of {out_base - out_rbac:.3f} points in task completion "
    f"({out_base:.3f} → {out_rbac:.3f}, -{(1 - out_rbac/out_base):.0%})."
)
