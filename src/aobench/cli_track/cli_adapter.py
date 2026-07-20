"""CLI / shell agent adapter — pure core (Feature 19).

A terminal agent (Claude Code, Codex CLI, Gemini CLI, mini-SWE-agent) is driven
against a task environment and emits a **stream of shell commands + outputs**.
This module translates that recorded stream into the universal ``Trace`` so the
existing scorer layer applies unchanged — each command becomes a ``shell``
tool-call step, and a destructive command (via the Feature 22 guard) flags the
trace ``hard_fail``.

The **container executor** that actually runs the commands (Docker/gVisor per
ADR 0006, Feature 18) is injected as a callable, so this core is pure and
testable without any sandbox: pass a recorded list of ``CommandRecord`` (offline
replay) or a ``command_source`` callable that produces them.
"""

from __future__ import annotations

import shlex
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Callable, Optional

from pydantic import BaseModel

from aobench.adapters.base import BaseAdapter
from aobench.cli_track.command_guard import score_command_stream
from aobench.schemas.trace import Observation, ToolCall, Trace, TraceStep
from aobench.utils.ids import make_trace_id

if TYPE_CHECKING:
    from aobench.runners.context import ExecutionContext


class CommandRecord(BaseModel):
    """One shell command the agent ran and what came back."""

    command: str
    stdout: str = ""
    exit_code: int = 0
    reasoning: Optional[str] = None
    denied: bool = False                 # blocked by the sandbox / RBAC before running
    denial_reason: Optional[str] = None


def _argv0(command: str) -> str:
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()
    return parts[0] if parts else ""


def build_cli_trace(
    context: "ExecutionContext",
    records: list[CommandRecord],
    *,
    final_answer: Optional[str] = None,
    own_job_ids: Optional[set[str]] = None,
) -> Trace:
    """Translate a recorded command stream into a scorer-ready ``Trace``.

    Destructive commands (Feature 22 guard) set ``hard_fail`` on the trace so the
    GovernanceScorer zeroes the run — judging the *commands actually issued*, not
    the agent's narration.
    """
    now = datetime.now(tz=timezone.utc)
    guard = score_command_stream([r.command for r in records], own_job_ids=own_job_ids)

    steps: list[TraceStep] = []
    for i, rec in enumerate(records, start=1):
        steps.append(
            TraceStep(
                step_id=i,
                step_type="tool_call",
                reasoning=rec.reasoning,
                tool_call=ToolCall(
                    tool_name="shell",
                    method=_argv0(rec.command),
                    arguments={"command": rec.command},
                ),
                observation=Observation(
                    content=rec.stdout,
                    error=(None if rec.exit_code == 0 and not rec.denied else
                           (rec.denial_reason or f"exit {rec.exit_code}")),
                    permission_denied=rec.denied,
                    denial_reason=rec.denial_reason,
                    metadata={"exit_code": rec.exit_code},
                ),
                timestamp=now,
            )
        )

    return Trace(
        trace_id=make_trace_id(),
        run_id=context.run_id,
        task_id=context.task.task_id,
        role=context.task.role,
        environment_id=context.env.metadata.environment_id,
        adapter_name="cli",
        steps=steps,
        final_answer=final_answer,
        start_time=now,
        end_time=now,
        total_tokens=0,
        hard_fail=guard.hard_fail,
    )


class CLIAdapter(BaseAdapter):
    """Adapter that records a CLI agent's command stream into a ``Trace``.

    ``command_source`` maps an ``ExecutionContext`` to the list of commands the
    agent ran. In production it wraps a container + terminal agent (Feature 18);
    in tests inject a plain callable returning ``CommandRecord`` objects — the
    trace-building and guard logic are identical either way.
    """

    name = "cli"

    def __init__(
        self,
        command_source: Callable[["ExecutionContext"], list[CommandRecord]],
        *,
        answer_source: Optional[Callable[["ExecutionContext"], str]] = None,
        own_job_ids: Optional[set[str]] = None,
    ) -> None:
        self._command_source = command_source
        self._answer_source = answer_source
        self._own_job_ids = own_job_ids

    def run(self, context: "ExecutionContext") -> Trace:
        records = self._command_source(context)
        answer = self._answer_source(context) if self._answer_source else None
        return build_cli_trace(context, records, final_answer=answer,
                               own_job_ids=self._own_job_ids)
