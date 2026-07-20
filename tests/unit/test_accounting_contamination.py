"""Tests for cost/energy accounting + contamination guard (Feature 26)."""

from __future__ import annotations

import pytest

from aobench.analysis.accounting import account_run, estimate_co2e_g, token_cost_usd
from aobench.analysis.contamination import check_contamination, output_diversity


# --------------------------------------------------------------------------- #
# accounting
# --------------------------------------------------------------------------- #
def test_token_cost():
    # 2000 in @ $0.005/1k + 1000 out @ $0.015/1k = 0.01 + 0.015 = 0.025
    c = token_cost_usd(2000, 1000, price_in_per_1k=0.005, price_out_per_1k=0.015)
    assert c == pytest.approx(0.025)


def test_estimate_co2e():
    assert estimate_co2e_g(1.0, grid_intensity_g_per_kwh=400.0) == pytest.approx(400.0)


def test_account_run_bundles_all():
    a = account_run(1000, 500, price_in_per_1k=0.01, price_out_per_1k=0.03)
    assert a.total_tokens == 1500
    assert a.cost_usd == pytest.approx(0.01 * 1 + 0.03 * 0.5)
    assert a.energy_kwh > 0
    assert a.co2e_g > 0
    assert a.energy_is_estimate is True


def test_account_run_without_prices():
    a = account_run(100, 50)
    assert a.cost_usd is None
    assert a.energy_kwh > 0


# --------------------------------------------------------------------------- #
# contamination
# --------------------------------------------------------------------------- #
def test_diversity_all_unique():
    assert output_diversity(["a", "b", "c"]) == 1.0


def test_diversity_all_identical():
    assert output_diversity(["same", "same", "same"]) == pytest.approx(1 / 3)


def test_diversity_empty():
    assert output_diversity([]) == 0.0


def test_contamination_low_diversity_flags_memorized():
    r = check_contamination(["x", "x", "x", "x"])
    assert r.likely_memorized is True


def test_contamination_high_diversity_clean():
    r = check_contamination(["a", "b", "c", "d"])
    assert r.likely_memorized is False


def test_contamination_canary_leak():
    r = check_contamination(
        ["the secret token AOB-CANARY-42 appears here"],
        canary="AOB-CANARY-42",
    )
    assert r.canary_leaked is True
    assert r.likely_memorized is True  # leak forces the flag


def test_contamination_needs_min_samples():
    # only 2 identical samples → not enough to flag on diversity alone
    r = check_contamination(["x", "x"])
    assert r.likely_memorized is False
