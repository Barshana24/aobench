"""Shared CLI helpers: corpus resolution and friendly not-found errors.

Every sub-command that needs the benchmark corpus goes through :func:`resolve_root`
so that AOBench behaves identically whether it runs from a source checkout, from an
installed wheel (corpus bundled as package data), or with ``$AOBENCH_BENCHMARK_ROOT``
pointing somewhere else entirely.

The ``require_*`` helpers turn a mistyped ID into a one-line message with "did you
mean" suggestions instead of a stack trace.
"""

from __future__ import annotations

import difflib
from pathlib import Path

import typer

from aobench.paths import BenchmarkDataNotFound, resolve_benchmark_root

__all__ = [
    "available_env_ids",
    "available_task_ids",
    "corpus_path",
    "require_env_dir",
    "require_task_spec",
    "resolve_bundle_root",
    "resolve_root",
    "suggest",
]


def resolve_root(benchmark_root: str | Path | None = "benchmark") -> Path:
    """Resolve the benchmark corpus root, or exit with an actionable message.

    ``"benchmark"`` (the CLI default) means "auto-detect"; any other value is an
    explicit path that must exist.
    """
    try:
        return resolve_benchmark_root(benchmark_root)
    except BenchmarkDataNotFound as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc


def resolve_bundle_root(benchmark_root: str | Path | None = "benchmark") -> Path:
    """Resolve a root that only needs to hold ``environments/``, not task specs.

    :func:`resolve_root` insists on ``tasks/specs`` as its marker, which is right for
    anything that runs or scores a task. Commands that only read or write environment
    bundles — ``aobench rbac ingest`` building a customer environment, for instance —
    legitimately operate on a directory that holds nothing else, so requiring the full
    corpus there would reject valid input. An explicit path is honoured verbatim; only
    the default falls back to full corpus auto-detection.
    """
    path = Path(benchmark_root) if benchmark_root else Path("benchmark")
    if (path / "environments").is_dir():
        return path
    return resolve_root(benchmark_root)


def corpus_path(value: str, default: str, relative: str) -> Path:
    """Resolve a CLI path option that points *inside* the benchmark corpus.

    An explicit ``value`` (anything other than ``default``) is honoured verbatim.
    The built-in ``default`` is only trusted when it exists relative to the CWD —
    otherwise it is rebuilt as ``<resolved corpus root>/<relative>``, so the option
    keeps working from an installed wheel or from outside a checkout.
    """
    path = Path(value)
    if value != default or path.exists():
        return path
    return resolve_root("benchmark") / relative


def available_task_ids(root: Path) -> list[str]:
    """Sorted task IDs present in ``root``, or an empty list if the dir is missing."""
    specs = root / "tasks" / "specs"
    if not specs.is_dir():
        return []
    return sorted(p.stem for p in specs.glob("*.json"))


def available_env_ids(root: Path) -> list[str]:
    """Sorted environment IDs present in ``root``, or an empty list if missing."""
    envs = root / "environments"
    if not envs.is_dir():
        return []
    return sorted(p.name for p in envs.iterdir() if p.is_dir() and p.name.startswith("env_"))


def suggest(value: str, candidates: list[str], limit: int = 3) -> list[str]:
    """Return up to ``limit`` candidates closest to ``value`` (case-insensitive).

    Ranked in three passes — prefix, then substring, then fuzzy near-miss — because
    ``difflib`` alone gets a truncated ID badly wrong. ``JOB_USR_00`` is an *equally*
    good match for all five ``JOB_USR_00N``, so which three come back is decided by
    ``get_close_matches``' internal heap order rather than by anything the user would
    recognise: it answered "did you mean JOB_USR_005, JOB_USR_004, JOB_USR_003?" and
    left out ``JOB_USR_001`` entirely. An ID the user literally typed a prefix of
    outranks a fuzzy match every time, and ordering within a pass is sorted so the
    answer is stable rather than an artefact of corpus iteration order.
    """
    if not candidates:
        return []
    needle = value.lower()
    ranked: list[str] = []

    def take(found: list[str]) -> None:
        ranked.extend(c for c in found if c not in ranked)

    take(sorted(c for c in candidates if c.lower().startswith(needle)))
    take(sorted(c for c in candidates if needle in c.lower()))
    lowered = {c.lower(): c for c in candidates}
    take(
        [lowered[m] for m in difflib.get_close_matches(needle, list(lowered), n=limit, cutoff=0.5)]
    )
    return ranked[:limit]


def _fail_unknown(kind: str, value: str, candidates: list[str], hint: str) -> None:
    lines = [f"Unknown {kind} '{value}'."]
    close = suggest(value, candidates)
    if close:
        lines.append("Did you mean: " + ", ".join(close) + "?")
    lines.append(f"Run `{hint}` to see all {len(candidates)} available.")
    typer.echo("\n".join(lines), err=True)
    raise typer.Exit(code=2)


def require_task_spec(root: Path, task_id: str) -> Path:
    """Return the task spec path, or exit with suggestions if it does not exist."""
    path = root / "tasks" / "specs" / f"{task_id}.json"
    if path.is_file():
        return path
    _fail_unknown("task ID", task_id, available_task_ids(root), "aobench list tasks")
    raise AssertionError("unreachable")  # pragma: no cover


def require_env_dir(root: Path, env_id: str) -> Path:
    """Return the environment bundle path, or exit with suggestions if missing."""
    path = root / "environments" / env_id
    if path.is_dir():
        return path
    _fail_unknown("environment ID", env_id, available_env_ids(root), "aobench list envs")
    raise AssertionError("unreachable")  # pragma: no cover
