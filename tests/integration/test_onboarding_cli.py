"""Integration tests for the first-use surface: quickstart, doctor, info, list.

These commands are what a brand-new user touches first, so the properties under test
are the onboarding promises themselves: they work with zero arguments, they work from
an arbitrary working directory (the corpus is resolved, never assumed to be `./benchmark`),
a mistyped ID produces a suggestion rather than a traceback, and a missing optional
extra never fails the command.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aobench.cli.main import app

runner = CliRunner()

pytestmark = pytest.mark.usefixtures("_cwd_outside_checkout")


@pytest.fixture
def _cwd_outside_checkout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, benchmark_root: Path):
    """Run each test from a scratch directory with no ``benchmark/`` above it.

    This is the installed-wheel situation. Without the explicit env var the resolver
    would have to fall back to package data, which is only populated in a built wheel,
    so point it at the repository corpus instead.
    """
    monkeypatch.setenv("AOBENCH_BENCHMARK_ROOT", str(benchmark_root))
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------


def test_doctor_passes_on_a_healthy_install() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0, result.output
    assert "AOBench looks healthy" in result.output


def test_doctor_exit_code_ignores_missing_optional_extras(monkeypatch: pytest.MonkeyPatch) -> None:
    """A laptop with no provider SDKs installed must still exit 0."""
    from aobench.cli import info_cmd

    optional = {name for name, _, _ in info_cmd._OPTIONAL_DEPS}
    real = info_cmd._installed
    monkeypatch.setattr(
        info_cmd, "_installed", lambda name: False if name in optional else real(name)
    )
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0, result.output
    assert "WARN" in result.output


def test_doctor_fails_when_the_corpus_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing corpus is a required failure — and must not reclassify the extras.

    Regression guard: the required/optional split used to be positional, so the four
    checks that disappear when the corpus is absent caused optional extras to be
    counted as required failures.
    """
    monkeypatch.setenv("AOBENCH_BENCHMARK_ROOT", "/nonexistent/benchmark")
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 1, result.output
    assert "1 required check(s) failed" in result.output


# ---------------------------------------------------------------------------
# info
# ---------------------------------------------------------------------------


def test_info_json_is_parseable_and_reports_the_corpus() -> None:
    result = runner.invoke(app, ["info", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["corpus"]["tasks"] > 0
    assert payload["corpus"]["environments"] > 0
    assert "aobench_version" in payload


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_list_tasks_from_outside_a_checkout() -> None:
    result = runner.invoke(app, ["list", "tasks"])
    assert result.exit_code == 0, result.output
    assert "JOB_USR_001" in result.output


def test_list_tasks_filters_compose() -> None:
    result = runner.invoke(app, ["list", "tasks", "--qcat", "JOB", "--role", "sysadmin", "--json"])
    assert result.exit_code == 0, result.output
    rows = json.loads(result.output)
    assert rows, "expected at least one JOB/sysadmin task"
    assert all(r["qcat"] == "JOB" and r["role"] == "sysadmin" for r in rows)


def test_list_tasks_ids_only_emits_bare_ids() -> None:
    result = runner.invoke(app, ["list", "tasks", "--ids-only"])
    assert result.exit_code == 0, result.output
    lines = [ln for ln in result.output.splitlines() if ln.strip()]
    assert lines
    assert all(" " not in ln for ln in lines)


def test_list_envs_reports_grounding() -> None:
    result = runner.invoke(app, ["list", "envs", "--json"])
    assert result.exit_code == 0, result.output
    rows = json.loads(result.output)
    assert {"synthetic", "real-M100"} >= {r["grounding"] for r in rows}


def test_list_adapters_needs_no_corpus(monkeypatch: pytest.MonkeyPatch) -> None:
    """Adapter discovery must work even before the corpus resolves."""
    monkeypatch.setenv("AOBENCH_BENCHMARK_ROOT", "/nonexistent/benchmark")
    result = runner.invoke(app, ["list", "adapters"])
    assert result.exit_code == 0, result.output
    assert "direct_qa" in result.output


# ---------------------------------------------------------------------------
# quickstart
# ---------------------------------------------------------------------------


def test_quickstart_runs_with_no_arguments(tmp_path: Path) -> None:
    """The headline promise: one command, no flags, no API key, a real score."""
    result = runner.invoke(app, ["quickstart", "--output", str(tmp_path / "runs")])
    assert result.exit_code == 0, result.output
    assert "Aggregate score:" in result.output
    assert "direct_qa" in result.output

    run_dirs = list((tmp_path / "runs").iterdir())
    assert len(run_dirs) == 1, "quickstart should produce exactly one run directory"
    assert (run_dirs[0] / "MANIFEST.json").is_file()


def test_quickstart_honours_an_explicit_task(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["quickstart", "--task", "JOB_SYS_001", "--output", str(tmp_path / "runs")]
    )
    assert result.exit_code == 0, result.output
    assert "JOB_SYS_001" in result.output


def test_quickstart_suggests_alternatives_for_a_mistyped_task(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["quickstart", "--task", "JOB_USR_01", "--output", str(tmp_path / "runs")]
    )
    assert result.exit_code == 2, result.output
    assert "JOB_USR_001" in result.output


# ---------------------------------------------------------------------------
# friendly errors on the main run path
# ---------------------------------------------------------------------------


def test_run_task_suggests_alternatives_for_a_mistyped_task(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["run", "task", "--task", "JOB_USR_01", "--env", "env_01", "--output", str(tmp_path)],
    )
    assert result.exit_code == 2, result.output
    assert "Unknown task ID" in result.output
    assert "JOB_USR_001" in result.output
    assert "Traceback" not in result.output


def test_run_task_suggests_alternatives_for_a_mistyped_env(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["run", "task", "--task", "JOB_USR_001", "--env", "env_99", "--output", str(tmp_path)],
    )
    assert result.exit_code == 2, result.output
    assert "Unknown environment ID" in result.output
    assert "Traceback" not in result.output


def test_run_task_resolves_the_corpus_from_outside_a_checkout(tmp_path: Path) -> None:
    """The exact command the README quick start prints, run from a wheel-like CWD."""
    result = runner.invoke(
        app,
        [
            "run", "task",
            "--task", "JOB_USR_001",
            "--env", "env_01",
            "--adapter", "direct_qa",
            "--output", str(tmp_path / "runs"),
            "--no-report",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "aggregate_score=" in result.output


def test_validate_benchmark_resolves_the_corpus_from_outside_a_checkout() -> None:
    result = runner.invoke(app, ["validate", "benchmark"])
    assert result.exit_code == 0, result.output
    assert "Validation passed." in result.output
