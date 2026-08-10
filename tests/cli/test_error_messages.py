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
    """A truncated ID must suggest the family it prefixes, starting at 001.

    This is the case that pure ``difflib`` ranking got wrong: every ``JOB_USR_00N``
    scores identically against ``JOB_USR_00``, so the three that came back were
    whichever the heap happened to surface — 005, 004, 003 — with 001 missing.
    """
    result = runner.invoke(
        app,
        ["run", "task", "--task", "JOB_USR_00", "--env", "env_01", "--adapter", "direct_qa"],
    )
    assert result.exit_code == 2
    assert "JOB_USR_001" in _output(result)
