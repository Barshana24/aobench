"""CLI / terminal agent-benchmarking track (Features 18–22).

Pure, container-free components:

- ``command_guard`` — F22 destructive-command / operational-safety guardrail scorer
  over a recorded shell command stream.
- ``slurm_shim``    — F20 core logic for the mock Slurm CLI shims
  (``squeue``/``sbatch``/``scontrol``/``sacct``) that read the same JSON state the
  mock ``SlurmTool`` uses, so real commands and mock tools share one ground truth.
- ``end_state``     — F21 Harbor-style end-state verification scorer that judges the
  final environment state (not the transcript) against expected assertions.
- ``cli_adapter``   — F19 CLI/shell agent adapter *pure core*: translates a recorded
  command stream into the universal ``Trace`` (guard-aware). The container executor
  (F18, ADR 0006) is injected, so this core is Docker-free and testable.

The containerized runner (F18, ADR 0006) is the heavier Docker-based lift that
supplies the executor for ``CLIAdapter``.
"""

from __future__ import annotations

from aobench.cli_track.cli_adapter import (
    CLIAdapter,
    CommandRecord,
    build_cli_trace,
)
from aobench.cli_track.command_guard import (
    CommandFinding,
    GuardResult,
    scan_commands,
    score_command_stream,
)
from aobench.cli_track.end_state import (
    EndStateAssertion,
    EndStateScore,
    score_end_state,
)

__all__ = [
    "scan_commands",
    "score_command_stream",
    "CommandFinding",
    "GuardResult",
    "score_end_state",
    "EndStateAssertion",
    "EndStateScore",
    "CLIAdapter",
    "CommandRecord",
    "build_cli_trace",
]
