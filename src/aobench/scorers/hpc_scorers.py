"""Futuristic HPC-operations scorers (Features 28 & 30).

- ``score_rca`` (F28): incident root-cause analysis — did the agent localize the
  correct root-cause *entity* (node/PSU/cooling-loop/GPU/network-policy) and
  propose an acceptable mitigation? Mitigation credit is **gated on entity
  correctness** (Cascading-Failure-Score logic): a right fix for the wrong cause
  earns nothing.
- ``score_carbon_aware_schedule`` (F30): did the agent shift deferrable jobs to
  low-carbon-intensity windows (within deadlines), vs a run-now baseline?
  Normalized against the carbon-optimal feasible schedule.
- ``score_log_evidence`` (F28 sub-scorer): did the agent cite the correct evidence
  log lines for its RCA (set-F1 over cited vs gold lines), complementing the
  root-cause-entity + mitigation scoring in ``score_rca``.

Pure/deterministic; a task harness supplies the gold labels and telemetry.
"""

from __future__ import annotations

import re

from pydantic import BaseModel


# --------------------------------------------------------------------------- #
# F28 — incident root-cause analysis
# --------------------------------------------------------------------------- #
class RCAScore(BaseModel):
    score: float
    entity_correct: bool
    mitigation_correct: bool
    notes: str = ""


def _norm(s: str) -> str:
    return " ".join(s.strip().lower().split())


def score_rca(
    predicted_entity: str,
    predicted_mitigation: str,
    *,
    gold_entity: str,
    acceptable_mitigations: list[str],
    entity_weight: float = 0.5,
) -> RCAScore:
    """Score an incident RCA answer (entity localization + mitigation)."""
    entity_correct = _norm(predicted_entity) == _norm(gold_entity)

    pm = _norm(predicted_mitigation)
    mitigation_correct = any(
        _norm(m) in pm or pm in _norm(m) for m in acceptable_mitigations if m.strip()
    )

    # CFS gating: mitigation only counts if the root cause is right.
    mit_credit = (1.0 - entity_weight) if (entity_correct and mitigation_correct) else 0.0
    ent_credit = entity_weight if entity_correct else 0.0
    score = round(ent_credit + mit_credit, 4)
    return RCAScore(
        score=score,
        entity_correct=entity_correct,
        mitigation_correct=mitigation_correct,
        notes=(
            f"entity={'✓' if entity_correct else '✗'} "
            f"mitigation={'✓' if mitigation_correct else '✗'}"
            + ("" if entity_correct else " (mitigation gated: wrong root cause)")
        ),
    )


# --------------------------------------------------------------------------- #
# F30 — carbon-aware scheduling
# --------------------------------------------------------------------------- #
class Job(BaseModel):
    job_id: str
    energy_kwh: float
    deadline_window: int   # latest window index the job may run in


class CarbonScore(BaseModel):
    score: float
    feasible: bool
    agent_carbon_g: float
    baseline_carbon_g: float
    optimal_carbon_g: float
    missed_deadlines: list[str] = []
    notes: str = ""


def _carbon(assignment: dict[str, int], jobs: dict[str, Job],
            intensity: list[float]) -> float:
    total = 0.0
    for jid, window in assignment.items():
        total += jobs[jid].energy_kwh * intensity[window]
    return total


def score_carbon_aware_schedule(
    jobs: list[Job],
    carbon_intensity: list[float],
    agent_assignment: dict[str, int],
    *,
    baseline_window: int = 0,
) -> CarbonScore:
    """Score a carbon-aware schedule vs a run-now baseline (gCO2 per kWh windows).

    Infeasible (a job assigned past its deadline, or an out-of-range window)
    scores 0. Otherwise: (baseline - agent) / (baseline - optimal), clipped [0,1].
    """
    jobmap = {j.job_id: j for j in jobs}
    n_windows = len(carbon_intensity)

    missed: list[str] = []
    for jid, job in jobmap.items():
        w = agent_assignment.get(jid)
        if w is None or w < 0 or w >= n_windows or w > job.deadline_window:
            missed.append(jid)

    baseline = _carbon({j.job_id: baseline_window for j in jobs}, jobmap, carbon_intensity)

    # Optimal feasible: each job → min-intensity window within its deadline.
    optimal_assign: dict[str, int] = {}
    for j in jobs:
        feasible_windows = range(0, min(j.deadline_window, n_windows - 1) + 1)
        optimal_assign[j.job_id] = min(feasible_windows, key=lambda w: carbon_intensity[w])
    optimal = _carbon(optimal_assign, jobmap, carbon_intensity)

    if missed:
        return CarbonScore(
            score=0.0, feasible=False, agent_carbon_g=float("nan"),
            baseline_carbon_g=baseline, optimal_carbon_g=optimal,
            missed_deadlines=missed,
            notes=f"infeasible: {len(missed)} job(s) miss deadline / bad window",
        )

    agent = _carbon(agent_assignment, jobmap, carbon_intensity)
    denom = baseline - optimal
    if denom <= 1e-12:
        score = 1.0  # no room to improve → any feasible schedule is optimal
    else:
        score = max(0.0, min(1.0, (baseline - agent) / denom))
    return CarbonScore(
        score=round(score, 4), feasible=True, agent_carbon_g=agent,
        baseline_carbon_g=baseline, optimal_carbon_g=optimal,
        notes=f"agent={agent:.1f} baseline={baseline:.1f} optimal={optimal:.1f}",
    )


# --------------------------------------------------------------------------- #
# F30 (part) — predictive maintenance
# --------------------------------------------------------------------------- #
class PMPrediction(BaseModel):
    entity: str
    predict_at: float   # time the agent raised the warning


class PMFailure(BaseModel):
    entity: str
    at: float           # time the entity actually failed


class PMScore(BaseModel):
    score: float
    precision: float
    recall: float
    lead_weighted_recall: float
    true_positives: int
    false_positives: int
    caught_failures: int
    total_failures: int
    notes: str = ""


def score_predictive_maintenance(
    predictions: list[PMPrediction],
    failures: list[PMFailure],
    *,
    min_lead: float = 1.0,
    max_lead: float = 24.0,
) -> PMScore:
    """Lead-time-weighted precision/recall for failure prediction.

    A prediction is a true positive if it names an entity that actually fails and
    was raised with an *actionable* lead time (``min_lead ≤ failure.at − predict_at
    ≤ max_lead``). Earlier warnings (larger lead, capped at ``max_lead``) earn more
    recall credit. Score = F1(precision, lead-weighted recall).
    """
    if not predictions and not failures:
        return PMScore(score=1.0, precision=1.0, recall=1.0, lead_weighted_recall=1.0,
                       true_positives=0, false_positives=0, caught_failures=0,
                       total_failures=0, notes="no predictions and no failures")

    def _lead(pred: PMPrediction, fail: PMFailure) -> float | None:
        if pred.entity != fail.entity:
            return None
        lead = fail.at - pred.predict_at
        return lead if (min_lead <= lead <= max_lead) else None

    # Precision: fraction of predictions that actionably match some failure.
    correct_preds = 0
    for p in predictions:
        if any(_lead(p, f) is not None for f in failures):
            correct_preds += 1
    n_pred = len(predictions)
    precision = (correct_preds / n_pred) if n_pred else (1.0 if not failures else 0.0)

    # Recall + lead-weighted recall: per failure, best actionable lead.
    caught = 0
    weight_sum = 0.0
    for f in failures:
        leads = [lead for p in predictions if (lead := _lead(p, f)) is not None]
        if leads:
            caught += 1
            best = max(leads)  # earliest warning → largest lead
            weight_sum += min(best, max_lead) / max_lead
    total_fail = len(failures)
    recall = (caught / total_fail) if total_fail else 1.0
    lead_weighted_recall = (weight_sum / total_fail) if total_fail else 1.0

    if precision + lead_weighted_recall <= 1e-12:
        score = 0.0
    else:
        score = 2 * precision * lead_weighted_recall / (precision + lead_weighted_recall)

    return PMScore(
        score=round(score, 4),
        precision=round(precision, 4),
        recall=round(recall, 4),
        lead_weighted_recall=round(lead_weighted_recall, 4),
        true_positives=correct_preds,
        false_positives=n_pred - correct_preds,
        caught_failures=caught,
        total_failures=total_fail,
        notes=f"precision={precision:.2f} lead_wt_recall={lead_weighted_recall:.2f}",
    )


# --------------------------------------------------------------------------- #
# F28 (sub-scorer) — log-analysis evidence localization
# --------------------------------------------------------------------------- #
class LogEvidenceScore(BaseModel):
    score: float          # F1 over cited vs gold evidence lines
    precision: float
    recall: float
    matched: list[str]
    extra: list[str]      # cited but not gold (noise)
    missed: list[str]     # gold but not cited
    notes: str = ""


def score_log_evidence(
    cited_lines: list[int | str], gold_lines: list[int | str]
) -> LogEvidenceScore:
    """Set-F1 over the log lines an agent cites as RCA evidence vs the gold lines.

    Rewards citing the correct evidence lines; citing irrelevant lines lowers
    precision, missing key lines lowers recall. Line identifiers may be indices
    or IDs — compared as strings.
    """
    cited = {str(x) for x in cited_lines}
    gold = {str(x) for x in gold_lines}

    if not gold and not cited:
        return LogEvidenceScore(score=1.0, precision=1.0, recall=1.0,
                                matched=[], extra=[], missed=[], notes="no evidence expected")

    matched = sorted(cited & gold)
    extra = sorted(cited - gold)
    missed = sorted(gold - cited)

    tp = len(matched)
    precision = tp / len(cited) if cited else 0.0
    recall = tp / len(gold) if gold else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return LogEvidenceScore(
        score=round(f1, 4), precision=round(precision, 4), recall=round(recall, 4),
        matched=matched, extra=extra, missed=missed,
        notes=f"tp={tp} extra={len(extra)} missed={len(missed)}",
    )


def find_evidence_lines(log_lines: list[str], patterns: list[str]) -> list[int]:
    """Helper: return indices of log lines matching any regex pattern (harness use)."""
    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
    return [i for i, line in enumerate(log_lines) if any(c.search(line) for c in compiled)]
