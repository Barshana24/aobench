"""Result attestation (Feature 25, ADR 0005).

Binds a run's result + trace + environment fingerprint into an **in-toto (ITE-6)**
statement and produces a **detached signature**. The default signer is a local
HMAC-SHA256 over the canonical JSON (offline, key from ``AOBENCH_ATTEST_KEY``);
**Sigstore keyless signing** is the recommended production path but requires
network + identity, so it is optional and layered on top.

Documented limitation (ADR 0005): a signature proves the *artifact* wasn't
tampered with — not that the numeric result is *correct* for the computation.
Pair attestation with deterministic replay (Feature 24) to verify correctness.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any, Optional

from pydantic import BaseModel

_STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
_PREDICATE_TYPE = "https://aobench.dev/attestations/run/v1"


def sha256_hex(data: Any) -> str:
    """sha256 of bytes/str, or of canonical JSON for other objects."""
    if isinstance(data, bytes):
        raw = data
    elif isinstance(data, str):
        raw = data.encode("utf-8")
    else:
        raw = _canonical(data).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def build_statement(
    subject_name: str,
    subject_sha256: str,
    predicate: dict[str, Any],
) -> dict[str, Any]:
    """Build an in-toto v1 statement (ITE-6)."""
    return {
        "_type": _STATEMENT_TYPE,
        "subject": [{"name": subject_name, "digest": {"sha256": subject_sha256}}],
        "predicateType": _PREDICATE_TYPE,
        "predicate": predicate,
    }


class Attestation(BaseModel):
    statement: dict[str, Any]
    signature: Optional[str] = None
    algorithm: str = "hmac-sha256"


def _key(key: Optional[str]) -> bytes:
    k = key if key is not None else os.environ.get("AOBENCH_ATTEST_KEY", "")
    return k.encode("utf-8")


def sign_statement(statement: dict[str, Any], *, key: Optional[str] = None) -> str:
    """Detached HMAC-SHA256 signature over the canonical statement."""
    return hmac.new(_key(key), _canonical(statement).encode("utf-8"), hashlib.sha256).hexdigest()


def verify_statement(
    statement: dict[str, Any], signature: str, *, key: Optional[str] = None
) -> bool:
    """Constant-time verify of a detached signature."""
    expected = sign_statement(statement, key=key)
    return hmac.compare_digest(expected, signature)


def attest_run(
    result: dict[str, Any],
    trace: dict[str, Any],
    *,
    run_id: str,
    env_manifest_sha256: Optional[str] = None,
    fingerprint: Optional[dict[str, Any]] = None,
    sign: bool = True,
    key: Optional[str] = None,
) -> Attestation:
    """Build (and optionally sign) an attestation for a completed run."""
    predicate = {
        "run_id": run_id,
        "result_sha256": sha256_hex(result),
        "trace_sha256": sha256_hex(trace),
        "env_manifest_sha256": env_manifest_sha256,
        "fingerprint": fingerprint or {},
    }
    statement = build_statement(
        subject_name=f"aobench-run:{run_id}",
        subject_sha256=sha256_hex(result),
        predicate=predicate,
    )
    signature = sign_statement(statement, key=key) if sign else None
    return Attestation(statement=statement, signature=signature)
