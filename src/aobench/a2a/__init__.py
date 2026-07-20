"""Agent-to-Agent (A2A) evaluation for AOBench (Features 12–17).

Pure, network-free components that let AOBench evaluate multi-agent
(orchestrator + worker) runs on the same grounded HPC tasks:

- ``schema``      — A2A objects (Agent Card, skills, delegation, multi-agent trace).
- ``conformance`` — F13 Agent Card conformance harness.
- ``scorers``     — F14 delegation-quality, F15 comms-cost, F16 failure-attribution.

Aligned to the Linux-Foundation A2A protocol. The live-network A2A *adapter*
(ADR 0004) is a later step; these components evaluate a recorded
``MultiAgentTrace`` and need no network.
"""

from __future__ import annotations

from aobench.a2a.adapter import (
    A2ADelegationEvent,
    A2AOrchestratorAdapter,
    build_multi_agent_trace,
)
from aobench.a2a.conformance import check_agent_card
from aobench.a2a.schema import (
    AgentCard,
    AgentSkill,
    DelegationRecord,
    MultiAgentTrace,
    TaskState,
)
from aobench.a2a.scorers import (
    attribute_failure,
    comms_cost,
    delegation_quality,
    score_card_poisoning_resistance,
    score_task_lifecycle,
)

__all__ = [
    "AgentCard",
    "AgentSkill",
    "DelegationRecord",
    "MultiAgentTrace",
    "TaskState",
    "check_agent_card",
    "delegation_quality",
    "comms_cost",
    "attribute_failure",
    "score_task_lifecycle",
    "score_card_poisoning_resistance",
    "build_multi_agent_trace",
    "A2ADelegationEvent",
    "A2AOrchestratorAdapter",
]
