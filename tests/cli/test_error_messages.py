"""Unknown task/env IDs produce a friendly one-line error, no traceback, exit code 2."""

from __future__ import annotations

from typer.testing import CliRunner

from aobench.cli.main import app

runner = CliRunner()


def _output(result) -> str:
    return (result.output or "") + (result.stderr or "")


def test_unknown_task_id_is_friendly():
    result = runner.invoke(
        app,
        ["run", "task", "--task", "NOPE_001", "--env", "env_01", "--adapter", "direct_qa"],
    )
    assert result.exit_code == 2
    assert "NOPE_001" in _output(result)
    assert "Traceback" not in _output(result)


def test_unknown_env_id_is_friendly():
    result = runner.invoke(
        app,
        ["run", "task", "--task", "AIOPS_DES_001", "--env", "env_nope", "--adapter", "direct_qa"],
    )
    assert result.exit_code == 2
    assert "env_nope" in _output(result)
    assert "Traceback" not in _output(result)


def test_close_match_is_suggested():
    result = runner.invoke(
        app,
        ["run", "task", "--task", "JOB_USR_00", "--env", "env_01", "--adapter", "direct_qa"],
    )
    assert result.exit_code == 2
    assert "JOB_USR_001" in _output(result)
