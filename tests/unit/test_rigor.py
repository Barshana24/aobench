"""Tests for pass^k + bootstrap CI rigor utilities (Feature 27)."""

from __future__ import annotations

import math

import pytest

from aobench.analysis.rigor import (
    bootstrap_ci,
    pass_hat_k,
    pass_k_from_scores,
    summarize_scores,
)


# --------------------------------------------------------------------------- #
# pass_hat_k
# --------------------------------------------------------------------------- #
def test_pass_hat_k_all_success():
    assert pass_hat_k(4, 4, 2) == 1.0


def test_pass_hat_k_partial():
    # C(2,2)/C(4,2) = 1/6
    assert pass_hat_k(4, 2, 2) == pytest.approx(1 / 6)


def test_pass_hat_k_below_k_is_zero():
    assert pass_hat_k(4, 1, 2) == 0.0


def test_pass_hat_k_k1_equals_frac():
    assert pass_hat_k(5, 3, 1) == pytest.approx(3 / 5)


def test_pass_hat_k_invalid():
    with pytest.raises(ValueError):
        pass_hat_k(2, 2, 0)
    with pytest.raises(ValueError):
        pass_hat_k(2, 2, 3)


def test_pass_k_from_scores():
    scores = [0.9, 0.8, 0.2, 0.95]  # 3 of 4 >= 0.5
    assert pass_k_from_scores(scores, 0.5, 2) == pytest.approx(pass_hat_k(4, 3, 2))


# --------------------------------------------------------------------------- #
# bootstrap_ci
# --------------------------------------------------------------------------- #
def test_bootstrap_ci_deterministic():
    vals = [0.1, 0.5, 0.9, 0.3, 0.7]
    a = bootstrap_ci(vals, seed=42)
    b = bootstrap_ci(vals, seed=42)
    assert a == b


def test_bootstrap_ci_single_value():
    assert bootstrap_ci([0.7]) == (0.7, 0.7)


def test_bootstrap_ci_empty_is_nan():
    lo, hi = bootstrap_ci([])
    assert math.isnan(lo) and math.isnan(hi)


def test_bootstrap_ci_brackets_mean():
    vals = [0.2, 0.4, 0.6, 0.8]
    lo, hi = bootstrap_ci(vals, seed=1)
    mean = sum(vals) / len(vals)
    assert lo <= mean <= hi


def test_bootstrap_ci_all_equal():
    assert bootstrap_ci([0.5, 0.5, 0.5]) == (0.5, 0.5)


# --------------------------------------------------------------------------- #
# summarize_scores
# --------------------------------------------------------------------------- #
def test_summarize_all_pass():
    s = summarize_scores([1.0, 0.9, 0.8], threshold=0.5, k=2)
    assert s.n == 3 and s.successes == 3
    assert s.pass_1 == 1.0
    assert s.pass_k == 1.0
    assert s.ci_low is not None and s.ci_high is not None


def test_summarize_all_fail():
    s = summarize_scores([0.1, 0.2, 0.0], threshold=0.5, k=2)
    assert s.successes == 0
    assert s.pass_1 == 0.0
    assert s.pass_k == 0.0


def test_summarize_deterministic_stdev_zero():
    s = summarize_scores([0.7, 0.7, 0.7], threshold=0.5, k=2)
    assert s.stdev == pytest.approx(0.0)
    assert s.pass_k == 1.0
