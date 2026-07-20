"""Phase 3 gold-consistency guard: the scored M100 gold_answers depend on these
qualitative facts holding in the generated telemetry, in both distribution-sampled
and --real-baselines mode. See scripts/build_m100_bundles.py:verify_gold_consistency."""
import sys
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _ROOT / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import build_m100_bundles as bb  # noqa: E402

_ENVS = _ROOT / "benchmark" / "environments"


def _df(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def test_committed_envs_satisfy_gold_consistency():
    """Every committed (distribution-sampled) env must satisfy its gold facts."""
    results = bb.check_all_envs(_ENVS)
    failures = {env: msgs for env, msgs in results.items() if msgs}
    assert not failures, f"gold-consistency failures: {failures}"
    assert set(results) == set(bb.GOLD_CHECKS)  # every env was checked


def test_exceeds_and_peers_below_detect_desync():
    """A hotspot that does not cross its threshold, and a peer that does, both fail."""
    checks = [
        {"kind": "exceeds", "node": "r3n7", "metric": "gpu3_core_temp", "threshold": 84.0},
        {"kind": "peers_below", "nodes": ["r3n0"], "metric": "gpu3_core_temp", "threshold": 84.0},
    ]
    # hotspot only reaches 70 (no throttle crossing); a peer reaches 90 (not isolated)
    df = _df([
        {"timestamp": "2022-07-15T13:00:00Z", "node_id": "r3n7", "metric_name": "gpu3_core_temp", "value": 70.0},
        {"timestamp": "2022-07-15T13:00:00Z", "node_id": "r3n0", "metric_name": "gpu3_core_temp", "value": 90.0},
    ])
    failures = bb.verify_gold_consistency(df, checks)
    assert len(failures) == 2


def test_collapse_and_dropout_detect_healthy_node():
    """A node whose metric never collapses, and one that never drops out, both fail."""
    checks = [
        {"kind": "collapses", "node": "r2n5", "metric": "total_power", "ratio": 0.6},
        {"kind": "drops_out", "node": "r7n2"},
    ]
    # r2n5 power stays flat (no collapse); r7n2 reports through the final snapshot
    df = _df([
        {"timestamp": "2022-07-20T10:00:00Z", "node_id": "r2n5", "metric_name": "total_power", "value": 700.0},
        {"timestamp": "2022-07-20T11:00:00Z", "node_id": "r2n5", "metric_name": "total_power", "value": 690.0},
        {"timestamp": "2022-07-20T10:00:00Z", "node_id": "r7n2", "metric_name": "total_power", "value": 500.0},
        {"timestamp": "2022-07-20T11:00:00Z", "node_id": "r7n2", "metric_name": "total_power", "value": 500.0},
    ])
    failures = bb.verify_gold_consistency(df, checks)
    assert len(failures) == 2


def test_collapse_and_dropout_pass_on_real_pattern():
    """The healthy-pattern checks pass when the node genuinely collapses / drops out."""
    checks = [
        {"kind": "collapses", "node": "r2n5", "metric": "total_power", "ratio": 0.6},
        {"kind": "drops_out", "node": "r7n2"},
    ]
    df = _df([
        {"timestamp": "2022-07-20T10:00:00Z", "node_id": "r2n5", "metric_name": "total_power", "value": 730.0},
        {"timestamp": "2022-07-20T11:00:00Z", "node_id": "r2n5", "metric_name": "total_power", "value": 260.0},
        # r7n2 stops early; another node reports through the snapshot
        {"timestamp": "2022-07-20T10:00:00Z", "node_id": "r7n2", "metric_name": "total_power", "value": 500.0},
        {"timestamp": "2022-07-20T11:00:00Z", "node_id": "r7n0", "metric_name": "total_power", "value": 500.0},
    ])
    failures = bb.verify_gold_consistency(df, checks)
    assert failures == []
