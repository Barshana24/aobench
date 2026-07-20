"""AOBench as an MCP **server** (FastMCP) — exposes the benchmark engine as
MCP tools + resources (spec-0004, Feature 6).

Distinct from ``aobench.adapters.mcp_client_adapter`` (AOBench as an MCP
*client* evaluating a server-under-test). They share no code (ADR 0004 §4).

Ships behind ``aobench[mcp]``; ``create_server()`` raises a clear, guarded error
when ``fastmcp`` is not installed.
"""

from __future__ import annotations

from aobench.server.mcp.server import FASTMCP_AVAILABLE, create_server

__all__ = ["create_server", "FASTMCP_AVAILABLE"]
