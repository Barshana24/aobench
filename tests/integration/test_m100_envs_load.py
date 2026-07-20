"""Integration tests: M100-grounded environments load and pass the fidelity gate."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from aobench.environment.fidelity_report import FidelityReport
from aobench.loaders.env_loader import load_environment

_ENVS = Path(__file__).resolve().parents[2] / "benchmark" / "environments"
_M100_ENVS = ["env_m100_01", "env_m100_02", "env_m100_03", "env_m100_04",
              "env_m100_05", "env_m100_06"]


@pytest.mark.parametrize("env_id", _M100_ENVS)
def test_m100_env_passes_full_fidelity_gate(env_id):
    """Load with the F1–F7 gate explicitly ENABLED (conftest sets SKIP=1 globally).

    This is the critical regression guard: real M100 power (~566W) would fail the
    F4 power-range check if it leaked into a CSV. Keeping power in the parquet must
    keep F4 (and F5) in the 'skipped' state.
    """
    prev = os.environ.pop("AOBENCH_SKIP_FIDELITY", None)
    try:
        report = FidelityReport(env_id=env_id, env_dir=_ENVS / env_id)
        report.run_all()
        assert report.passed, [
            f"{r.validator_id}: {r.message}" for r in report.results if not r.passed
        ]
        by_id = {r.validator_id: r for r in report.results}
        assert "no power files" in by_id["F4"].message      # power stays in parquet
        assert by_id["F5"].passed
    finally:
        if prev is not None:
            os.environ["AOBENCH_SKIP_FIDELITY"] = prev


@pytest.mark.parametrize("env_id", _M100_ENVS)
def test_m100_env_telemetry_is_m100_grounded(env_id):
    """The loaded bundle exposes M100 vocabulary in the canonical telemetry schema."""
    import pandas as pd

    bundle = load_environment(_ENVS / env_id)
    assert bundle.metadata.cluster_name == "marconi100"

    df = pd.read_parquet(_ENVS / env_id / "telemetry" / "telemetry_timeseries.parquet")
    assert {"timestamp", "node_id", "metric_name", "value", "unit"} <= set(df.columns)
    assert "plugin" in df.columns
    # Plugins are real M100 plugin names (envs mix ipmi_pub + ganglia_pub + vertiv_pub).
    assert set(df["plugin"].unique()) <= {"ipmi_pub", "ganglia_pub", "vertiv_pub", "nagios_pub"}
    # M100 node naming r{rack}n{slot} and real IPMI metric names.
    assert all(n[0] == "r" and "n" in n for n in df["node_id"].unique())
    assert "total_power" in set(df["metric_name"].unique())
