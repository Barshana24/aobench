"""Filesystem helpers."""

from __future__ import annotations

from pathlib import Path

from aobench.paths import resolve_benchmark_root as _resolve

__all__ = ["resolve_benchmark_root"]


def resolve_benchmark_root(given: str | Path | None = None) -> Path:
    """Find the benchmark corpus root.

    Thin backwards-compatible alias for :func:`aobench.paths.resolve_benchmark_root`,
    which is the single source of truth: it honours ``$AOBENCH_BENCHMARK_ROOT``, then a
    source checkout found by walking up from the CWD, then the copy bundled inside the
    installed package. Raises :class:`aobench.paths.BenchmarkDataNotFound` if none
    resolve.
    """
    return _resolve(given)
