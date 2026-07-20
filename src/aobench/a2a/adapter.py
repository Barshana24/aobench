"""A2A orchestrator/worker adapter — pure core (Feature 12).

In a live A2A run, an orchestrator discovers worker agents (via their Agent
Cards), delegates sub-tasks to them over the network, and assembles their
results. This module translates a **recorded delegation-event stream** into the
``MultiAgentTrace`` the A2A scorers (F14–F17: delegation quality, comms cost,
failure attribution, lifecycle) already consume.

The live A2A HTTP transport (JSON-RPC / SSE against worker Agent Cards) is
injected as a ``delegation_source`` callable, so this core is network-free and
testable: pass a recorded list of ``A2ADelegationEvent`` (offline replay) or a
callable that produces them from a live orchestration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from pydantic import BaseModel

from aobench.a2a.schema import DelegationRecord, MultiAgentTrace, TaskState

if TYPE_CHECKING:
    from aobench.runners.context import ExecutionContext

_FAILURE_STATES = {TaskState.FAILED, TaskState.REJECTED}


class A2ADelegationEvent(BaseModel):
    """One recorded orchestrator→worker delegation (the 'wire' record)."""

    subtask: str
    to_agent: str
    from_agent: str = "orchestrator"
    messages: int = 1
    tokens: int = 0
    result_state: TaskState = TaskState.COMPLETED
    caused_failure: bool = False


def build_multi_agent_trace(
    task_id: str,
    events: list[A2ADelegationEvent],
    *,
    orchestrator: str = "orchestrator",
    gold_delegation_map: Optional[dict[str, str]] = None,
    gold_failure_agent: Optional[str] = None,
) -> MultiAgentTrace:
    """Translate a recorded delegation-event stream into a ``MultiAgentTrace``.

    ``run_failed`` is inferred when any delegation ends in a failure state or is
    flagged as the ground-truth culprit — so the F16 attribution scorer has a
    consistent signal without the caller setting it separately.
    """
    delegations = [
        DelegationRecord(
            subtask=e.subtask,
            to_agent=e.to_agent,
            from_agent=e.from_agent,
            messages=e.messages,
            tokens=e.tokens,
            result_state=e.result_state,
            caused_failure=e.caused_failure,
        )
        for e in events
    ]
    # Preserve first-seen order of workers (stable, not sorted — routing order matters).
    workers: list[str] = []
    for e in events:
        if e.to_agent not in workers:
            workers.append(e.to_agent)

    run_failed = any(e.caused_failure or e.result_state in _FAILURE_STATES for e in events)

    return MultiAgentTrace(
        task_id=task_id,
        orchestrator=orchestrator,
        workers=workers,
        delegations=delegations,
        gold_delegation_map=gold_delegation_map or {},
        run_failed=run_failed,
        gold_failure_agent=gold_failure_agent,
    )


class A2AOrchestratorAdapter:
    """Adapter that records an A2A orchestration into a ``MultiAgentTrace``.

    ``delegation_source`` maps an ``ExecutionContext`` to the delegation events
    the orchestrator produced. In production it wraps live A2A calls to worker
    Agent Cards; in tests inject a plain callable — the trace-building logic is
    identical. Not a ``BaseAdapter`` (A2A is a distinct modality producing a
    ``MultiAgentTrace``, not the single-agent ``Trace`` — see ADR 0004).
    """

    name = "a2a"

    def __init__(
        self,
        delegation_source: Callable[["ExecutionContext"], list[A2ADelegationEvent]],
        *,
        gold_delegation_map: Optional[dict[str, str]] = None,
        gold_failure_agent: Optional[str] = None,
        orchestrator: str = "orchestrator",
    ) -> None:
        self._delegation_source = delegation_source
        self._gold_delegation_map = gold_delegation_map
        self._gold_failure_agent = gold_failure_agent
        self._orchestrator = orchestrator

    def run_multi_agent(self, context: "ExecutionContext") -> MultiAgentTrace:
        events = self._delegation_source(context)
        return build_multi_agent_trace(
            context.task.task_id,
            events,
            orchestrator=self._orchestrator,
            gold_delegation_map=self._gold_delegation_map,
            gold_failure_agent=self._gold_failure_agent,
        )
