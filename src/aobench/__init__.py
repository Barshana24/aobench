"""AOBench — Benchmark framework for evaluating AI agents in HPC environments."""

from importlib.metadata import PackageNotFoundError, version as _version

try:
    # Single source of truth is pyproject.toml; reading it back from the
    # installed distribution metadata means the two can never drift.
    __version__ = _version("aobench")
except PackageNotFoundError:  # pragma: no cover - only when running from a raw checkout
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
