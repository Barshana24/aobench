"""Unit tests for the M100-grounded bundle importer (scripts/build_m100_bundles.py)."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pytest

# The importer lives under scripts/, not the installed package.
_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from build_m100_bundles import (  # noqa: E402
    apply_step,
    load_reference_distributions,
    synthesize_node_telemetry,
)

UTC = timezone.utc
_CANONICAL_COLS = {"timestamp", "node_id", "metric_name", "value", "unit"}


@pytest.fixture(scope="module")
def dist() -> dict:
    return load_reference_distributions()


def test_reference_has_real_ipmi_metrics(dist):
    # Distributions are fit from the real M100 IPMI sample.
    for m in ("total_power", "ambient", "gpu3_core_temp", "ps0_input_power"):
        assert m in dist, f"missing real M100 metric {m}"
        assert dist[m]["plugin"] == "ipmi_pub"
    assert dist["total_power"]["unit"] == "W"
    # gpu2 does not exist on M100 nodes (GPUs are labeled 0,1,3,4).
    assert "gpu2_core_temp" not in dist


def test_synthesize_is_deterministic(dist):
    nodes = ["r0n0", "r0n1"]
    metrics = ["total_power", "ambient"]
    snap = datetime(2022, 7, 15, 14, 0, 0, tzinfo=UTC)
    a = synthesize_node_telemetry(nodes, metrics, 2, snap, dist, np.random.default_rng(388))
    b = synthesize_node_telemetry(nodes, metrics, 2, snap, dist, np.random.default_rng(388))
    assert a.equals(b)


def test_synthesize_schema_and_plugin_column(dist):
    df = synthesize_node_telemetry(
        ["r0n0"], ["total_power"], 1,
        datetime(2022, 7, 15, 14, 0, 0, tzinfo=UTC), dist, np.random.default_rng(1),
    )
    assert _CANONICAL_COLS <= set(df.columns)        # canonical schema preserved
    assert "plugin" in df.columns                    # M100 provenance column
    assert set(df["plugin"].unique()) == {"ipmi_pub"}
    assert str(df["timestamp"].dtype).startswith("datetime64")


def test_synthesized_values_within_clamp_bounds(dist):
    metric = "total_power"
    df = synthesize_node_telemetry(
        ["r0n0", "r0n1", "r0n2"], [metric], 6,
        datetime(2022, 7, 15, 14, 0, 0, tzinfo=UTC), dist, np.random.default_rng(7),
    )
    lo, hi = dist[metric]["lo"], dist[metric]["hi"]
    assert df["value"].min() >= lo
    assert df["value"].max() <= hi


def test_apply_step_overlays_labeled_value(dist):
    snap = datetime(2022, 7, 20, 11, 0, 0, tzinfo=UTC)
    df = synthesize_node_telemetry(
        ["r10n4", "r10n1"], ["total_power"], 2, snap, dist, np.random.default_rng(2),
    )
    df = apply_step(df, "r10n4", "total_power", snap, 0.5, 1400.0)
    last = df[df["node_id"] == "r10n4"].sort_values("timestamp")["value"].iloc[-1]
    assert last == pytest.approx(1400.0)
    # Peer node is untouched by the perturbation.
    peer_last = df[df["node_id"] == "r10n1"].sort_values("timestamp")["value"].iloc[-1]
    assert peer_last != pytest.approx(1400.0)
