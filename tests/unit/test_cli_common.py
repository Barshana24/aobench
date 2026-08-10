"""Unit tests for the shared CLI corpus-resolution and suggestion helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
import typer

from aobench.cli._common import (
    available_env_ids,
    available_task_ids,
    corpus_path,
    require_env_dir,
    require_task_spec,
    resolve_root,
    suggest,
)


@pytest.fixture
def elsewhere(tmp_path: Path) -> Path:
    """A working directory with no ``benchmark/`` in it or above it inside tmp_path."""
    path = tmp_path / "elsewhere"
    path.mkdir()
    return path


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    """A minimal but structurally valid benchmark corpus."""
    root = tmp_path / "benchmark"
    specs = root / "tasks" / "specs"
    specs.mkdir(parents=True)
    (specs / "JOB_USR_001.json").write_text("{}", encoding="utf-8")
    (specs / "MON_SYS_002.json").write_text("{}", encoding="utf-8")
    (root / "environments" / "env_01").mkdir(parents=True)
    (root / "environments" / "env_02").mkdir(parents=True)
    (root / "configs").mkdir()
    return root


def test_available_ids_are_sorted(corpus: Path) -> None:
    assert available_task_ids(corpus) == ["JOB_USR_001", "MON_SYS_002"]
    assert available_env_ids(corpus) == ["env_01", "env_02"]


def test_available_ids_tolerate_a_missing_directory(tmp_path: Path) -> None:
    assert available_task_ids(tmp_path) == []
    assert available_env_ids(tmp_path) == []


def test_suggest_finds_a_near_miss() -> None:
    assert "JOB_USR_001" in suggest("JOB_USR_01", ["JOB_USR_001", "MON_SYS_002"])


def test_suggest_falls_back_to_substring_for_a_prefix() -> None:
    """`difflib` scores a short prefix poorly, so a substring pass has to cover it."""
    assert suggest("MON", ["JOB_USR_001", "MON_SYS_002"]) == ["MON_SYS_002"]


def test_suggest_is_case_insensitive() -> None:
    assert suggest("job_usr_001", ["JOB_USR_001"]) == ["JOB_USR_001"]


def test_suggest_on_an_empty_corpus_returns_nothing() -> None:
    assert suggest("anything", []) == []


def test_require_task_spec_returns_the_path(corpus: Path) -> None:
    assert require_task_spec(corpus, "JOB_USR_001").is_file()


def test_require_task_spec_exits_with_a_suggestion(corpus: Path, capsys) -> None:
    with pytest.raises(typer.Exit) as exc:
        require_task_spec(corpus, "JOB_USR_01")
    assert exc.value.exit_code == 2
    err = capsys.readouterr().err
    assert "Unknown task ID" in err
    assert "JOB_USR_001" in err


def test_require_env_dir_exits_with_a_suggestion(corpus: Path, capsys) -> None:
    with pytest.raises(typer.Exit) as exc:
        require_env_dir(corpus, "env_99")
    assert exc.value.exit_code == 2
    assert "Unknown environment ID" in capsys.readouterr().err


def test_resolve_root_honours_the_env_var(
    corpus: Path, monkeypatch: pytest.MonkeyPatch, elsewhere: Path
) -> None:
    monkeypatch.setenv("AOBENCH_BENCHMARK_ROOT", str(corpus))
    monkeypatch.chdir(elsewhere)
    assert resolve_root("benchmark") == corpus


def test_resolve_root_exits_when_nothing_resolves(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys
) -> None:
    monkeypatch.setenv("AOBENCH_BENCHMARK_ROOT", str(tmp_path / "missing"))
    monkeypatch.chdir(tmp_path)
    with pytest.raises(typer.Exit) as exc:
        resolve_root("benchmark")
    assert exc.value.exit_code == 2
    assert "Could not locate" in capsys.readouterr().err


def test_corpus_path_honours_an_explicit_value(tmp_path: Path) -> None:
    explicit = tmp_path / "somewhere" / "else.yaml"
    assert corpus_path(str(explicit), "benchmark/configs/x.yaml", "configs/x.yaml") == explicit


def test_corpus_path_prefers_an_existing_relative_default(
    corpus: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Inside a checkout the historical relative default must keep winning."""
    monkeypatch.chdir(corpus.parent)
    assert corpus_path(
        "benchmark/tasks/specs", "benchmark/tasks/specs", "tasks/specs"
    ) == Path("benchmark/tasks/specs")


def test_corpus_path_rebuilds_the_default_from_the_resolved_root(
    corpus: Path, monkeypatch: pytest.MonkeyPatch, elsewhere: Path
) -> None:
    """Outside a checkout the same default has to point into the resolved corpus."""
    monkeypatch.setenv("AOBENCH_BENCHMARK_ROOT", str(corpus))
    monkeypatch.chdir(elsewhere)
    assert corpus_path(
        "benchmark/tasks/specs", "benchmark/tasks/specs", "tasks/specs"
    ) == corpus / "tasks" / "specs"
