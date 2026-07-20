"""Agent Card conformance harness (Feature 13).

Validates a submitted Agent Card against the A2A schema as a registration gate:
required fields present, well-formed endpoint URL, at least one declared skill,
coherent capabilities, and (optionally) a present signature. Returns a report
rather than raising, so a registry can surface all problems at once.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ValidationError

from aobench.a2a.schema import AgentCard


class ConformanceReport(BaseModel):
    passed: bool
    errors: list[str] = []
    warnings: list[str] = []


def _valid_url(url: str) -> bool:
    return url.startswith(("http://", "https://")) and "." in url[8:]


def check_agent_card(card: Any) -> ConformanceReport:
    """Validate an Agent Card (dict or AgentCard). Never raises."""
    errors: list[str] = []
    warnings: list[str] = []

    # Coerce dict → AgentCard (schema-level validation).
    if isinstance(card, dict):
        try:
            card = AgentCard.model_validate(card)
        except ValidationError as exc:
            return ConformanceReport(passed=False, errors=[f"schema: {exc.error_count()} field error(s)"])
    elif not isinstance(card, AgentCard):
        return ConformanceReport(passed=False, errors=["not an AgentCard or dict"])

    # Required fields.
    if not card.name.strip():
        errors.append("missing required field: name")
    if not card.version.strip():
        errors.append("missing required field: version")

    # Endpoint URL.
    if not card.url.strip():
        errors.append("missing required field: url")
    elif not _valid_url(card.url):
        errors.append(f"malformed url: {card.url!r}")

    # Skills.
    if not card.skills:
        errors.append("no skills declared (an agent must advertise ≥1 skill)")
    else:
        seen_ids = set()
        for sk in card.skills:
            if not sk.id.strip():
                errors.append("skill with empty id")
            if sk.id in seen_ids:
                errors.append(f"duplicate skill id: {sk.id!r}")
            seen_ids.add(sk.id)

    # Capabilities coherence (warn, not fail).
    if not card.capabilities:
        warnings.append("no capabilities advertised")

    # Auth / signature (warn).
    if not card.security_schemes:
        warnings.append("no securitySchemes declared (agent will be treated as unauthenticated)")
    if card.signature is None:
        warnings.append("card is unsigned (integrity/authenticity cannot be verified)")

    return ConformanceReport(passed=not errors, errors=errors, warnings=warnings)
