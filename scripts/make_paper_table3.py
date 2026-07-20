"""make_paper_table3.py — Table 3: Role × QCAT breakdown for three models.

Shows Qwen3.6 35B-A3B (best), GPT-4o (mid-tier, well-known), and
Gemma4 31B (worst) to illustrate how role/QCAT sensitivity varies across
the capability spectrum.

Input:  data/runs/v02_dev/<model>/run_*/results/*.json
        data/runs/v02_dev_ollama/<model>/run_*/results/*.json
Output: Markdown table (Table 3a only — no delta sub-table).

Usage:
    uv run python scripts/make_paper_table3.py
"""

import json
import pathlib
import statistics
from collections import defaultdict

V02_DEV        = pathlib.Path("data/runs/v02_dev")
V02_DEV_OLLAMA = pathlib.Path("data/runs/v02_dev_ollama")

ROLES = [
    "scientific_user",
    "sysadmin",
    "facility_admin",
    "researcher",
    "system_designer",
]
ROLE_LABELS = {
    "scientific_user": "Scientific User",
    "sysadmin":        "Sysadmin",
    "facility_admin":  "Facility Admin",
    "researcher":      "Researcher",
    "system_designer": "System Designer",
}
QCATS = ["AIOPS", "ARCH", "DATA", "DOCS", "ENERGY", "FAC", "JOB", "MON", "SEC", "USR"]

# Three representative models: (token, base_dir, display_label)
MODELS = [
    ("qwen3.6:35b-a3b", V02_DEV_OLLAMA, "Qwen3.6 35B-A3B (MoE)"),  # best
    ("gpt-4o",          V02_DEV,        "GPT-4o"),                   # mid
    ("gemma4:31b",      V02_DEV_OLLAMA, "Gemma4 31B"),               # worst
]


def load_results(token: str, base: pathlib.Path) -> list[dict]:
    model_dir = base / token
    run_dirs = sorted(model_dir.glob("run_*"))
    if not run_dirs:
        return []
    latest = run_dirs[-1]
    results = []
    for f in sorted(latest.glob("results/*.json")):
        try:
            results.append(json.loads(f.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            pass
    return results


def build_slices(results: list[dict]) -> dict[str, dict[str, dict]]:
    """Return slices[role][qcat] = {mean_score, count}."""
    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in results:
        role  = r.get("role") or ""
        qcat  = r.get("task_category") or ""
        score = r.get("aggregate_score")
        if role and qcat and score is not None:
            buckets[role][qcat].append(float(score))
    return {
        role: {
            qcat: {"mean_score": statistics.mean(scores), "count": len(scores)}
            for qcat, scores in qcat_map.items()
        }
        for role, qcat_map in buckets.items()
    }


def cell_str(slices: dict, role: str, qcat: str) -> str:
    s = slices.get(role, {}).get(qcat)
    if s is None:
        return "—"
    return f"{s['mean_score']:.3f} (n={s['count']})"


# ── Load ──────────────────────────────────────────────────────────────────────

all_slices: list[tuple[str, dict]] = []
for token, base, label in MODELS:
    results = load_results(token, base)
    all_slices.append((label, build_slices(results)))

# Determine which QCATs are actually present across all three models
present_qcats = sorted({
    q
    for _, slices in all_slices
    for role_data in slices.values()
    for q in role_data
})
# Preserve canonical order from QCATS, restrict to present
ordered_qcats = [q for q in QCATS if q in present_qcats]
if not ordered_qcats:
    ordered_qcats = present_qcats  # fallback

# ── Markdown ─────────────────────────────────────────────────────────────────

print("## Table 3 — Mean Score by Role × QCAT (three representative models)\n")

header = "| Model | Role | " + " | ".join(ordered_qcats) + " |"
sep    = "|------|------|" + "|".join(["------"] * len(ordered_qcats)) + "|"
print(header)
print(sep)

for label, slices in all_slices:
    first_row = True
    for role in ROLES:
        if not any(slices.get(role, {}).get(q) for q in ordered_qcats):
            continue
        cells = [cell_str(slices, role, q) for q in ordered_qcats]
        model_col = label if first_row else ""
        print(f"| {model_col} | {ROLE_LABELS.get(role, role)} | " + " | ".join(cells) + " |")
        first_row = False
    print("|" + " | ".join([""] * (len(ordered_qcats) + 2)) + "|")  # blank separator row

# ── LaTeX ─────────────────────────────────────────────────────────────────────

ncols = "ll" + "c" * len(ordered_qcats)

print("\n\n## LaTeX\n")
print(r"\begin{table*}[t]")
print(r"\centering")
print(r"\small")
print(
    r"\caption{Mean aggregate score by Role~$\times$~QCAT for three representative models: "
    r"best (Qwen3.6 35B-A3B), mid-tier (GPT-4o), and weakest (Gemma4 31B). "
    r"Cell counts in parentheses.}"
)
print(r"\label{tab:role_qcat}")
print(f"\\begin{{tabular}}{{{ncols}}}")
print(r"\toprule")
print("Model & Role & " + " & ".join(ordered_qcats) + r" \\")
print(r"\midrule")

first_model = True
for label, slices in all_slices:
    if not first_model:
        print(r"\midrule")
    first_model = False
    first_row = True
    for role in ROLES:
        role_slices = slices.get(role, {})
        if not any(role_slices.get(q) for q in ordered_qcats):
            continue
        cells = []
        for qcat in ordered_qcats:
            s = role_slices.get(qcat)
            if s is None:
                cells.append(r"\,---")
            else:
                cells.append(f"{s['mean_score']:.3f} ($n$={s['count']})")
        model_col = label if first_row else ""
        role_label = ROLE_LABELS.get(role, role)
        print(f"{model_col} & {role_label} & " + " & ".join(cells) + r" \\")
        first_row = False

print(r"\bottomrule")
print(r"\end{tabular}")
print(r"\end{table*}")
