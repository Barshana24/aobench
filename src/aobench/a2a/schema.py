"""A2A protocol objects (subset) + AOBench multi-agent trace model.

Field names follow the Linux-Foundation Agent2Agent spec. Version-sensitive
details (the ``/.well-known/agent-card.json`` path, task-state enum spelling per
binding) should be verified against the live spec before wiring a network
adapter; the shapes here are for evaluation of recorded runs.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskState(str, Enum):
    """A2A task lifecycle states."""

    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input_required"
    AUTH_REQUIRED = "auth_required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    REJECTED = "rejected"


TERMINAL_STATES = {TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELED, TaskState.REJECTED}
INTERRUPTED_STATES = {TaskState.INPUT_REQUIRED, TaskState.AUTH_REQUIRED}


class AgentSkill(BaseModel):
    id: str
    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)


class AgentCard(BaseModel):
    """Machine-readable agent identity + capability advertisement."""

    name: str
    description: str = ""
    version: str = ""
    url: str = ""
    provider: dict[str, Any] = Field(default_factory=dict)
    capabilities: dict[str, Any] = Field(default_factory=dict)
    skills: list[AgentSkill] = Field(default_factory=list)
    security_schemes: dict[str, Any] = Field(default_factory=dict)
    signature: Optional[str] = None


class DelegationRecord(BaseModel):
    """One orchestrator→worker delegation within a multi-agent run."""

    subtask: str                     # logical subtask / skill requested
    to_agent: str                    # worker the orchestrator delegated to
    from_agent: str = "orchestrator"
    messages: int = 1                # A2A messages exchanged for this delegation
    tokens: int = 0                  # tokens spent on this delegation
    result_state: TaskState = TaskState.COMPLETED
    caused_failure: bool = False     # ground-truth: did this delegation cause the run to fail


class MultiAgentTrace(BaseModel):
    """A recorded orchestrator + worker A2A run for evaluation."""

    task_id: str
    orchestrator: str = "orchestrator"
    workers: list[str] = Field(default_factory=list)
    delegations: list[DelegationRecord] = Field(default_factory=list)
    # Gold routing: subtask → the worker that *should* handle it.
    gold_delegation_map: dict[str, str] = Field(default_factory=dict)
    run_failed: bool = False
    # Ground-truth attribution label: which agent caused the failure (for F16 scoring).
    gold_failure_agent: Optional[str] = None

    def total_messages(self) -> int:
        return sum(d.messages for d in self.delegations)

    def total_tokens(self) -> int:
        return sum(d.tokens for d in self.delegations)
