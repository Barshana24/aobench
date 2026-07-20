"""merge_clear_reports.py — Compute CLEAR for all 15 models (GPT + Ollama).

Loads all model results, runs build_clear_report() with all models together
(so L_norm is cross-model comparable), then nulls cost fields for local-inference
(Ollama) models whose API cost is zero or undefined.

Outputs: data/reports/v02_clear_report_merged.json

Usage:
    uv run python scripts/merge_clear_reports.py
"""

from __future__ import annotations

import json
from pathlib import Path

from aobench.schemas.result import BenchmarkResult
from aobench.reports.clear_report import build_clear_report

# ── Model definitions ──────────────────────────────────────────────────────────

V02_DEV        = Path("data/runs/v02_dev")
V02_DEV_OLLAMA = Path("data/runs/v02_dev_ollama")

# (model_token, base_dir)
# Order: GPT API models first, then Ollama, then baseline
MODEL_ENTRIES: list[tuple[str, Path]] = [
    ("gpt-4o",                  V02_DEV),
    ("gpt-4o-mini",             V02_DEV),
    ("qwen3.6:35b-a3b",         V02_DEV_OLLAMA),
    ("qwen3.5:122b",            V02_DEV_OLLAMA),
    ("mistral-nemo:latest",     V02_DEV_OLLAMA),
    ("GLM-4.7-Flash:latest",    V02_DEV_OLLAMA),
    ("nemotron-3-super:latest", V02_DEV_OLLAMA),
    ("nemotron3:33b",           V02_DEV_OLLAMA),
    ("devstral-small-2:24b",    V02_DEV_OLLAMA),
    ("qwen3-coder-next:latest", V02_DEV_OLLAMA),
    ("gemma4:e4b",              V02_DEV_OLLAMA),
    ("gpt-oss:latest",          V02_DEV_OLLAMA),
    ("gpt-oss:20b",             V02_DEV_OLLAMA),
    ("mistral-small:24b",       V02_DEV_OLLAMA),
    ("gemma4:31b",              V02_DEV_OLLAMA),
    ("direct_qa",               V02_DEV),
]

# These models have no API cost — null out their cost columns after CLEAR compute.
OLLAMA_TOKENS: set[str] = {
    "qwen3.6:35b-a3b", "qwen3.5:122b", "mistral-nemo:latest", "GLM-4.7-Flash:latest",
    "nemotron-3-super:latest", "nemotron3:33b", "devstral-small-2:24b",
    "qwen3-coder-next:latest", "gemma4:e4b", "gpt-oss:latest", "gpt-oss:20b",
    "mistral-small:24b", "gemma4:31b",
}

MIN_RESULTS = 50

# Tasks excluded from primary scoring due to a known spec/data defect
# (AIOPS_USR_001: ownership mismatch hard-fails every agentic system). Kept in
# sync with load_results.py and compute_stats.py.
EXCLUDE_FROM_SCORING = {"AIOPS_USR_001"}


def load_results(token: str, base: Path) -> list[BenchmarkResult]:
    """Load BenchmarkResult objects from the latest run directory for a model."""
    model_dir = base / token
    if not model_dir.exists():
        return []
    run_dirs = sorted(model_dir.glob("run_*"))
    if not run_dirs:
        return []
    latest = run_dirs[-1]
    results_dir = latest / "results"
    if not results_dir.exists():
        return []
    results: list[BenchmarkResult] = []
    for f in sorted(results_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("task_id") in EXCLUDE_FROM_SCORING:
                continue  # known spec/data defect — excluded from primary scoring
            results.append(BenchmarkResult.model_validate(data))
        except Exception as exc:
            print(f"  WARN: could not parse {f.name}: {exc}")
    return results


# ── Load ───────────────────────────────────────────────────────────────────────

model_results: dict[str, list[BenchmarkResult]] = {}

for token, base in MODEL_ENTRIES:
    results = load_results(token, base)
    if len(results) < MIN_RESULTS:
        print(f"SKIP {token}: {len(results)} results (< {MIN_RESULTS})")
        continue
    model_results[token] = results
    print(f"OK   {token}: {len(results)} results")

print(f"\nLoaded {len(model_results)} models.")

# ── Hardware-cost proxy for local (Ollama) models ─────────────────────────────
# Open-weight models incur no API fee, which would leave the CLEAR Cost axis
# defined over only the two API-billed models (a degenerate 2-point min-max).
# To let Cost/CLEAR span the full panel we assign each local run a hardware-time
# proxy: cost = wall-clock latency x an assumed cloud GPU rate (single GPU).
# This is illustrative; set PROXY_GPU_USD_PER_HR to your facility's rate. The
# proxy is documented as such in the paper (Table 2 caption).
PROXY_GPU_USD_PER_HR = 2.00          # single-GPU cloud-equivalent reference rate
_proxy_per_sec = PROXY_GPU_USD_PER_HR / 3600.0
for token in OLLAMA_TOKENS:
    for r in model_results.get(token, []):
        if r.latency_seconds is not None:
            r.cost_estimate_usd = round(r.latency_seconds * _proxy_per_sec, 6)

# ── Compute CLEAR for ALL models together ──────────────────────────────────────
# Running all models in one call gives cross-model L_norm and C_norm. With the
# hardware-cost proxy above, C_norm, CNA, CPS, and the CLEAR composite are now
# defined for every tool-using model, not just the API-billed pair.

report = build_clear_report(model_results)

def _sort_key(entry: dict) -> tuple:
    t = entry["model"]
    is_baseline = (t == "direct_qa")
    is_ollama   = (t in OLLAMA_TOKENS)
    clear       = entry.get("clear_score")
    e           = entry.get("E") or 0.0
    # Groups: (0) API models with CLEAR, (1) Ollama/no-CLEAR, (2) baseline
    group = 2 if is_baseline else (1 if (is_ollama or clear is None) else 0)
    sort_clear = -(clear or 0.0)
    sort_e     = -e
    return (group, sort_clear, sort_e)

report["leaderboard"].sort(key=_sort_key)
for i, entry in enumerate(report["leaderboard"], start=1):
    entry["rank"] = i

# ── Write output ───────────────────────────────────────────────────────────────

OUT_PATH = Path("data/reports/v02_clear_report_merged.json")
OUT_PATH.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
print(f"\nWrote {OUT_PATH}  ({len(model_results)} models)")
print("\nLeaderboard:")
for entry in report["leaderboard"]:
    clear = entry.get("clear_score")
    e     = entry.get("E")
    tag   = f"CLEAR={clear:.4f}" if clear is not None else f"E={e:.4f}" if e is not None else "---"
    print(f"  {entry['rank']:2d}. {entry['model']:35s}  {tag}")
