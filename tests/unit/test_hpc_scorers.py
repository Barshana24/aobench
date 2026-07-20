"""Tests for futuristic HPC scorers: incident RCA (F28) + carbon-aware (F30)."""

from __future__ import annotations

from aobench.scorers.hpc_scorers import (
    Job,
    PMFailure,
    PMPrediction,
    find_evidence_lines,
    score_carbon_aware_schedule,
    score_log_evidence,
    score_predictive_maintenance,
    score_rca,
)


# --------------------------------------------------------------------------- #
# F28 — incident RCA
# --------------------------------------------------------------------------- #
def test_rca_both_correct():
    r = score_rca("node042", "drain node042 and reschedule",
                  gold_entity="node042",
                  acceptable_mitigations=["drain the node", "drain node042 and reschedule"])
    assert r.score == 1.0
    assert r.entity_correct and r.mitigation_correct


def test_rca_entity_right_mitigation_wrong():
    r = score_rca("node042", "reboot the whole rack",
                  gold_entity="node042",
                  acceptable_mitigations=["drain the node"])
    assert r.entity_correct is True
    assert r.mitigation_correct is False
    assert r.score == 0.5


def test_rca_entity_wrong_gates_mitigation():
    # right fix text but wrong root cause → cascading zero
    r = score_rca("node999", "drain the node",
                  gold_entity="node042",
                  acceptable_mitigations=["drain the node"])
    assert r.entity_correct is False
    assert r.score == 0.0
    assert "gated" in r.notes


def test_rca_case_insensitive_entity():
    r = score_rca("  Node042 ", "drain the node", gold_entity="node042",
                  acceptable_mitigations=["drain the node"])
    assert r.entity_correct is True


# --------------------------------------------------------------------------- #
# F30 — carbon-aware scheduling
# --------------------------------------------------------------------------- #
def _jobs():
    return [
        Job(job_id="j1", energy_kwh=10.0, deadline_window=3),
        Job(job_id="j2", energy_kwh=5.0, deadline_window=3),
    ]


# intensity: window 0 is dirtiest, window 2 cleanest
_INTENSITY = [500.0, 300.0, 100.0, 400.0]


def test_carbon_optimal_schedule_scores_1():
    # both jobs shifted to the cleanest feasible window (2)
    r = score_carbon_aware_schedule(_jobs(), _INTENSITY, {"j1": 2, "j2": 2})
    assert r.feasible is True
    assert r.score == 1.0


def test_carbon_run_now_scores_0():
    # baseline is window 0 → agent doing the same earns 0 improvement
    r = score_carbon_aware_schedule(_jobs(), _INTENSITY, {"j1": 0, "j2": 0})
    assert r.feasible is True
    assert r.score == 0.0


def test_carbon_partial_improvement():
    r = score_carbon_aware_schedule(_jobs(), _INTENSITY, {"j1": 1, "j2": 1})
    assert 0.0 < r.score < 1.0


def test_carbon_missed_deadline_infeasible():
    jobs = [Job(job_id="j1", energy_kwh=10.0, deadline_window=1)]
    r = score_carbon_aware_schedule(jobs, _INTENSITY, {"j1": 3})  # past deadline
    assert r.feasible is False
    assert r.score == 0.0
    assert "j1" in r.missed_deadlines


def test_carbon_out_of_range_window_infeasible():
    r = score_carbon_aware_schedule(_jobs(), _INTENSITY, {"j1": 99, "j2": 2})
    assert r.feasible is False


def test_carbon_no_room_to_improve():
    flat = [200.0, 200.0, 200.0, 200.0]
    r = score_carbon_aware_schedule(_jobs(), flat, {"j1": 1, "j2": 2})
    assert r.score == 1.0  # denom ~0 → any feasible schedule optimal


# --------------------------------------------------------------------------- #
# F30 — predictive maintenance
# --------------------------------------------------------------------------- #
def test_pm_perfect_prediction():
    preds = [PMPrediction(entity="node01", predict_at=76.0)]  # 24h lead → full weight
    fails = [PMFailure(entity="node01", at=100.0)]
    r = score_predictive_maintenance(preds, fails)
    assert r.precision == 1.0
    assert r.recall == 1.0
    assert r.lead_weighted_recall == 1.0
    assert r.score == 1.0


def test_pm_missed_failure():
    r = score_predictive_maintenance([], [PMFailure(entity="node01", at=100.0)])
    assert r.recall == 0.0
    assert r.score == 0.0
    assert r.caught_failures == 0


def test_pm_false_positive_lowers_precision():
    preds = [
        PMPrediction(entity="node01", predict_at=90.0),   # actionable (10h lead)
        PMPrediction(entity="node99", predict_at=90.0),   # never fails → FP
    ]
    fails = [PMFailure(entity="node01", at=100.0)]
    r = score_predictive_maintenance(preds, fails)
    assert r.true_positives == 1
    assert r.false_positives == 1
    assert r.precision == 0.5


def test_pm_too_late_prediction_not_credited():
    # predicted at 101 but failure at 100 → negative lead, not actionable
    preds = [PMPrediction(entity="node01", predict_at=101.0)]
    fails = [PMFailure(entity="node01", at=100.0)]
    r = score_predictive_maintenance(preds, fails)
    assert r.caught_failures == 0
    assert r.score == 0.0


def test_pm_short_lead_reduces_weight():
    # 2h lead vs 24h cap → lower lead-weighted recall than a full-lead prediction
    preds = [PMPrediction(entity="node01", predict_at=98.0)]
    fails = [PMFailure(entity="node01", at=100.0)]
    r = score_predictive_maintenance(preds, fails)
    assert r.recall == 1.0
    assert r.lead_weighted_recall < 1.0


def test_pm_no_events_is_1():
    r = score_predictive_maintenance([], [])
    assert r.score == 1.0


# --------------------------------------------------------------------------- #
# F28 sub-scorer — log-analysis evidence localization
# --------------------------------------------------------------------------- #
def test_log_evidence_perfect():
    r = score_log_evidence([12, 47], [12, 47])
    assert r.score == 1.0
    assert r.precision == 1.0 and r.recall == 1.0


def test_log_evidence_extra_lowers_precision():
    r = score_log_evidence([12, 47, 99], [12, 47])  # 99 is noise
    assert r.recall == 1.0
    assert r.precision < 1.0
    assert "99" in r.extra


def test_log_evidence_missed_lowers_recall():
    r = score_log_evidence([12], [12, 47])  # missed 47
    assert r.precision == 1.0
    assert r.recall == 0.5
    assert "47" in r.missed


def test_log_evidence_disjoint_zero():
    r = score_log_evidence([1, 2], [3, 4])
    assert r.score == 0.0


def test_log_evidence_string_ids():
    r = score_log_evidence(["oom.log:5"], ["oom.log:5"])
    assert r.score == 1.0


def test_log_evidence_none_expected():
    r = score_log_evidence([], [])
    assert r.score == 1.0


def test_find_evidence_lines():
    logs = [
        "INFO job started",
        "ERROR oom-killer invoked on node042",
        "INFO checkpoint written",
        "WARN memory pressure high",
    ]
    hits = find_evidence_lines(logs, [r"oom-killer", r"memory pressure"])
    assert hits == [1, 3]
