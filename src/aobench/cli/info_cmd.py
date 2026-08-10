"""``aobench info`` and ``aobench doctor`` — answer "is my install sane?" in one command.

``info`` is the thing to paste into a bug report: version, corpus location, corpus
size, and which optional extras are importable. ``doctor`` is the same inspection
turned into pass/fail checks with a suggested fix for each failure.
"""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import typer

from aobench import __version__
from aobench.paths import BenchmarkDataNotFound, resolve_benchmark_root

# (import name, pip extra, what it unlocks)
_OPTIONAL_DEPS: list[tuple[str, str, str]] = [
    ("openai", "openai", "the `openai:` adapter"),
    ("anthropic", "anthropic", "the `anthropic:` adapter"),
    ("mcp", "mcp", "the `mcp:` adapter and `aobench serve mcp`"),
    ("fastapi", "rest", "`aobench serve rest`"),
    ("langfuse", "langfuse", "trace export to Langfuse"),
]

# Hard dependencies declared in pyproject. Absence means a broken install, not a
# missing feature, so these are checked as required rather than listed as extras.
_CORE_DEPS: list[str] = ["pydantic", "yaml", "typer", "rich", "pandas"]


def _corpus_summary(root: Path) -> dict[str, Any]:
    spec_dir = root / "tasks" / "specs"
    env_dir = root / "environments"
    specs = sorted(spec_dir.glob("*.json")) if spec_dir.is_dir() else []
    envs = (
        sorted(p for p in env_dir.iterdir() if p.is_dir() and p.name.startswith("env_"))
        if env_dir.is_dir()
        else []
    )
    return {
        "root": str(root),
        "tasks": len(specs),
        "tasks_grounded_m100": sum(1 for p in specs if p.name.startswith("M100_")),
        "environments": len(envs),
        "environments_grounded_m100": sum(1 for p in envs if p.name.startswith("env_m100_")),
        "scoring_profiles": str(root / "configs" / "scoring_profiles.yaml"),
    }


def _installed(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):  # pragma: no cover - defensive
        return False


def info(
    as_json: bool = typer.Option(False, "--json", help="Emit JSON — good for bug reports."),
    benchmark_root: str = typer.Option("benchmark", "--benchmark-root"),
) -> None:
    """Print the AOBench version, corpus location, and optional-extra status."""
    payload: dict[str, Any] = {
        "aobench_version": __version__,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "executable": sys.executable,
        "extras": {name: _installed(name) for name, _, _ in _OPTIONAL_DEPS},
        "env": {
            key: ("set" if os.environ.get(key) else "unset")
            for key in (
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "AZURE_OPENAI_API_KEY",
                "LANGFUSE_PUBLIC_KEY",
                "AOBENCH_BENCHMARK_ROOT",
                "AOBENCH_UNLOCK_TEST",
            )
        },
    }
    try:
        payload["corpus"] = _corpus_summary(resolve_benchmark_root(benchmark_root))
    except BenchmarkDataNotFound as exc:
        payload["corpus"] = {"error": str(exc)}

    if as_json:
        typer.echo(json.dumps(payload, indent=2))
        return

    typer.echo(f"AOBench {payload['aobench_version']}")
    typer.echo(f"  Python      {payload['python']}  ({payload['executable']})")
    typer.echo(f"  Platform    {payload['platform']}")
    corpus = payload["corpus"]
    if "error" in corpus:
        typer.echo(f"  Corpus      NOT FOUND — {corpus['error']}")
    else:
        typer.echo(f"  Corpus      {corpus['root']}")
        typer.echo(
            f"              {corpus['tasks']} tasks "
            f"({corpus['tasks_grounded_m100']} grounded in real Marconi100 data)"
        )
        typer.echo(
            f"              {corpus['environments']} environments "
            f"({corpus['environments_grounded_m100']} grounded)"
        )
    typer.echo("  Extras      " + ", ".join(
        f"{name}{'' if ok else ' (missing)'}" for name, ok in payload["extras"].items()
    ))
    typer.echo("  Env vars    " + ", ".join(f"{k}={v}" for k, v in payload["env"].items()))


def _checks(benchmark_root: str) -> Iterator[tuple[bool, bool, str, str]]:
    """Yield ``(required, passed, label, remedy)`` for every diagnostic.

    Each check carries its own ``required`` flag rather than relying on position:
    when the corpus is missing, four fewer required checks are produced, and a
    positional split would silently reclassify optional extras as hard failures.
    """
    yield (
        True,
        sys.version_info >= (3, 10),
        f"Python {sys.version.split()[0]} (requires >= 3.10)",
        "Install Python 3.12 and recreate the virtualenv.",
    )

    yield (
        True,
        __version__ != "0.0.0+unknown",
        f"aobench package metadata readable (version {__version__})",
        "Run `pip install -e .` — AOBench is on sys.path but not installed as a distribution.",
    )

    missing_core = [m for m in _CORE_DEPS if not _installed(m)]
    yield (
        True,
        not missing_core,
        "core dependencies importable"
        + (f" — missing: {', '.join(missing_core)}" if missing_core else ""),
        "Reinstall AOBench: `pip install -e .` (or `uv sync`).",
    )

    try:
        root = resolve_benchmark_root(benchmark_root)
        summary = _corpus_summary(root)
        yield (True, True, f"Benchmark corpus found at {root}", "")
        yield (
            True,
            summary["tasks"] > 0,
            f"{summary['tasks']} task specs load",
            "The corpus directory exists but holds no task specs — re-clone the repository.",
        )
        yield (
            True,
            summary["environments"] > 0,
            f"{summary['environments']} environment bundles present",
            "No environment bundles — re-clone, or set AOBENCH_BENCHMARK_ROOT.",
        )
        yield (
            True,
            Path(summary["scoring_profiles"]).is_file(),
            "scoring_profiles.yaml present",
            "Missing benchmark/configs/scoring_profiles.yaml — nothing can be scored.",
        )
    except BenchmarkDataNotFound as exc:
        yield (
            True,
            False,
            "Benchmark corpus found",
            f"{exc}\n    Set AOBENCH_BENCHMARK_ROOT=/path/to/benchmark, "
            "or run from a source checkout.",
        )

    for name, extra, unlocks in _OPTIONAL_DEPS:
        ok = _installed(name)
        yield (
            False,
            ok,
            f"`{name}` {'installed' if ok else 'not installed'} — {'unlocks' if ok else 'would unlock'} {unlocks}",
            f"Optional. Install with `pip install 'aobench[{extra}]'` if you need {unlocks}.",
        )


def doctor(
    benchmark_root: str = typer.Option("benchmark", "--benchmark-root"),
    strict: bool = typer.Option(
        False, "--strict", help="Exit non-zero on optional-extra warnings too."
    ),
) -> None:
    """Diagnose a broken or partial AOBench installation.

    Required checks failing exit 1. Missing optional extras are reported as warnings
    and exit 0 unless ``--strict`` is passed, because most users legitimately install
    only the adapters they use.
    """
    results = list(_checks(benchmark_root))
    required = [(ok, label, remedy) for is_req, ok, label, remedy in results if is_req]
    optional = [(ok, label, remedy) for is_req, ok, label, remedy in results if not is_req]

    failures = 0
    warnings = 0

    typer.echo("Required")
    for ok, label, remedy in required:
        typer.echo(f"  {'PASS' if ok else 'FAIL'}  {label}")
        if not ok:
            failures += 1
            if remedy:
                typer.echo(f"        → {remedy}")

    typer.echo("\nOptional")
    for ok, label, remedy in optional:
        typer.echo(f"  {'PASS' if ok else 'WARN'}  {label}")
        if not ok:
            warnings += 1
            if remedy:
                typer.echo(f"        → {remedy}")

    typer.echo("")
    if failures:
        typer.echo(f"{failures} required check(s) failed. AOBench will not run correctly.")
        raise typer.Exit(code=1)
    if warnings and strict:
        typer.echo(f"{warnings} optional extra(s) missing and --strict was passed.")
        raise typer.Exit(code=1)
    typer.echo(
        f"AOBench looks healthy. {warnings} optional extra(s) not installed — "
        "that is fine unless you need them."
    )
