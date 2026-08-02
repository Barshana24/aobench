"""Resolution of the benchmark data root.

The benchmark corpus (task specs, environment snapshots, configs) lives in a
``benchmark/`` directory. When AOBench runs from a source checkout that directory
sits at the repo root; when AOBench is installed from a wheel it is bundled inside
the package as ``aobench`` package data. This module resolves the right location
regardless of how AOBench was installed, in this order:

1. ``$AOBENCH_BENCHMARK_ROOT`` if set (explicit override).
2. A ``benchmark/`` directory found by walking up from the current working
   directory — so a source checkout works from any subdirectory.
3. The copy bundled inside the installed package (``aobench`` package data).

If none resolve, :func:`resolve_benchmark_root` raises
:class:`BenchmarkDataNotFound` with an actionable message.
"""

from __future__ import annotations

import os
from importlib import resources
from pathlib import Path

__all__ = [
    "BenchmarkDataNotFound",
    "ENV_VAR",
    "default_benchmark_root",
    "resolve_benchmark_root",
]

ENV_VAR = "AOBENCH_BENCHMARK_ROOT"

#: Marker used to recognize a genuine benchmark root (avoids false positives).
_MARKER = Path("tasks") / "specs"


class BenchmarkDataNotFound(FileNotFoundError):
    """Raised when the benchmark corpus cannot be located."""

    def __init__(self, tried: list[str] | None = None) -> None:
        hint = (
            "Could not locate the AOBench benchmark corpus (the 'benchmark/' "
            "directory with tasks/specs). Fix this by either:\n"
            "  - running from a clone of https://github.com/MSKazemi/aobench "
            "(the corpus is at ./benchmark), or\n"
            f"  - setting {ENV_VAR}=/path/to/benchmark, or\n"
            "  - passing --benchmark /path/to/benchmark on the CLI."
        )
        if tried:
            hint += "\nLocations tried: " + ", ".join(tried)
        super().__init__(hint)


def _looks_like_root(path: Path) -> bool:
    return (path / _MARKER).is_dir()


def _bundled_root() -> Path | None:
    """Return the benchmark corpus bundled inside the installed package, if any."""
    try:
        data = resources.files("aobench") / "benchmark"
    except (ModuleNotFoundError, TypeError):  # pragma: no cover - defensive
        return None
    candidate = Path(str(data))
    return candidate if _looks_like_root(candidate) else None


def default_benchmark_root() -> Path | None:
    """Best-effort benchmark root, or ``None`` if it cannot be found.

    Never raises — callers that require the data should use
    :func:`resolve_benchmark_root` instead.
    """
    env = os.environ.get(ENV_VAR)
    if env:
        return Path(env).expanduser()

    cwd = Path.cwd().resolve()
    for base in (cwd, *cwd.parents):
        candidate = base / "benchmark"
        if _looks_like_root(candidate):
            return candidate

    return _bundled_root()


def resolve_benchmark_root(value: str | Path | None = None) -> Path:
    """Resolve ``value`` to an existing benchmark root, or raise.

    ``value`` is what the caller/CLI provided. The sentinel default ``"benchmark"``
    (or ``None``) means "auto-detect": try the env var, a checkout, then the
    bundled copy. Any other value is honored as an explicit path and must exist.
    """
    tried: list[str] = []

    if value is not None and str(value) != "benchmark":
        explicit = Path(value).expanduser()
        if _looks_like_root(explicit):
            return explicit
        tried.append(str(explicit))
        raise BenchmarkDataNotFound(tried)

    resolved = default_benchmark_root()
    if resolved is not None and _looks_like_root(resolved):
        return resolved

    if os.environ.get(ENV_VAR):
        tried.append(f"{ENV_VAR}={os.environ[ENV_VAR]}")
    tried.append(str(Path.cwd() / "benchmark"))
    tried.append("bundled package data")
    raise BenchmarkDataNotFound(tried)
