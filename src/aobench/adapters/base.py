"""Base adapter interface — all agent backends implement this."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from aobench.schemas.trace import Trace

if TYPE_CHECKING:
    from aobench.runners.context import ExecutionContext


class BaseAdapter(ABC):
    """Adapter wraps an LLM backend and produces a Trace for a given ExecutionContext."""

    name: str  # Must be set as class attribute by subclasses

    @abstractmethod
    def run(self, context: "ExecutionContext") -> Trace:
        """Run the agent on the context and return a complete trace."""
        ...
