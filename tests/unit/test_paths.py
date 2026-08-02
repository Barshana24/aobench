"""Tests for benchmark-root resolution (aobench.paths)."""

from __future__ import annotations

from pathlib import Path

import pytest

from aobench.paths import (
    ENV_VAR,
    BenchmarkDataNotFound,
    default_benchmark_root,
    resolve_benchmark_root,
)


def _make_root(base: Path) -> Path:
    """Create a minimal benchmark-root layout under ``base`` and return it."""
    root = base / "benchmark"
    (root / "tasks" / "specs").mkdir(parents=True)
    (root / "environments").mkdir(parents=True)
    return root


def test_env_var_takes_precedence(tmp_path, monkeypatch):
    root = _make_root(tmp_path)
    monkeypatch.setenv(ENV_VAR, str(root))
    # Even from an unrelated CWD, the env var wins.
    monkeypatch.chdir(tmp_path.parent if tmp_path.parent.exists() else tmp_path)
    assert resolve_benchmark_root("benchmark") == root
    assert default_benchmark_root() == root


def test_cwd_autodetect_walks_up(tmp_path, monkeypatch):
    root = _make_root(tmp_path)
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    monkeypatch.delenv(ENV_VAR, raising=False)
    monkeypatch.chdir(nested)
    # Resolves the benchmark/ dir several levels up from the CWD.
    assert resolve_benchmark_root("benchmark") == root


def test_explicit_path_is_honored(tmp_path, monkeypatch):
    root = _make_root(tmp_path)
    monkeypatch.delenv(ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)
    assert resolve_benchmark_root(str(root)) == root


def test_explicit_missing_path_raises(tmp_path, monkeypatch):
    monkeypatch.delenv(ENV_VAR, raising=False)
    missing = tmp_path / "nope"
    with pytest.raises(BenchmarkDataNotFound):
        resolve_benchmark_root(str(missing))


def test_not_found_raises_actionable(tmp_path, monkeypatch):
    # Empty CWD, no env var, no ./benchmark — but the installed package may still
    # carry a bundled copy, so only assert the raise when nothing is found.
    monkeypatch.delenv(ENV_VAR, raising=False)
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.chdir(empty)
    if default_benchmark_root() is None:
        with pytest.raises(BenchmarkDataNotFound) as exc:
            resolve_benchmark_root("benchmark")
        assert ENV_VAR in str(exc.value)
