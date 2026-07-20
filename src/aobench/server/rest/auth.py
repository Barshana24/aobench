"""API-key auth + minimal rate limiting for the REST surface (spec-0003 R3/R4).

Identity model: an API key maps to an HPC role. Keys are configured via the
``AOBENCH_API_KEYS`` env var as a comma-separated ``key:role`` list, e.g.
``AOBENCH_API_KEYS="k1:hpc_user,k2:admin"``. When the var is unset, the API runs
in open (dev) mode and every request resolves to the ``admin`` role — this makes
local use frictionless while production deployments simply set the var.

Rate limiting is a fixed-window in-memory counter (per key), generous by default
and configured via ``AOBENCH_RATE_LIMIT_PER_MIN``. A Redis-backed limiter is
deferred to the ``aobench[serve]`` extra (ADR 0002).
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Identity:
    tenant: str
    role: str


def _configured_keys() -> dict[str, str]:
    raw = os.environ.get("AOBENCH_API_KEYS", "").strip()
    keys: dict[str, str] = {}
    if not raw:
        return keys
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair or ":" not in pair:
            continue
        key, role = pair.split(":", 1)
        keys[key.strip()] = role.strip() or "hpc_user"
    return keys


def resolve_identity(api_key: str | None) -> Identity | None:
    """Return an Identity for the given key, or None if auth fails.

    In open (dev) mode (no keys configured) any request resolves to admin.
    """
    keys = _configured_keys()
    if not keys:
        return Identity(tenant="dev", role="admin")
    if api_key and api_key in keys:
        return Identity(tenant=api_key[:8], role=keys[api_key])
    return None


# --------------------------------------------------------------------------- #
# Minimal fixed-window in-memory rate limiter
# --------------------------------------------------------------------------- #
_WINDOW_SECONDS = 60
_buckets: dict[str, tuple[int, int]] = {}  # key -> (window_start, count)


def _limit_per_min() -> int:
    try:
        return int(os.environ.get("AOBENCH_RATE_LIMIT_PER_MIN", "10000"))
    except ValueError:
        return 10000


def check_rate_limit(key: str, *, now: float | None = None) -> bool:
    """Return True if the request is within the per-minute budget for ``key``."""
    limit = _limit_per_min()
    if limit <= 0:
        return True
    t = int(now if now is not None else time.time())
    window = t - (t % _WINDOW_SECONDS)
    start, count = _buckets.get(key, (window, 0))
    if start != window:
        start, count = window, 0
    count += 1
    _buckets[key] = (start, count)
    return count <= limit


def reset_rate_limits() -> None:
    """Test helper — clear all rate-limit buckets."""
    _buckets.clear()
