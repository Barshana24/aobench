"""OTLP binding for the pure span converter (spec-0005).

Maps ``SpanData`` trees to real OpenTelemetry spans and exports them over OTLP.
No-ops cleanly when the ``otel`` extra is absent (R6). Langfuse is the default
endpoint; any OTLP backend works via ``OTEL_EXPORTER_OTLP_ENDPOINT``.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from aobench.exporters.otel.converter import SpanData, trace_to_spans
from aobench.schemas.result import BenchmarkResult
from aobench.schemas.trace import Trace

try:
    from opentelemetry import trace as _ot_trace
    from opentelemetry.sdk.trace import TracerProvider

    OTEL_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only when extra absent
    OTEL_AVAILABLE = False

__all__ = ["OTEL_AVAILABLE", "export_run", "emit_spans", "trace_to_spans", "SpanData"]


def _content_capture_enabled() -> bool:
    return os.environ.get("AOBENCH_OTEL_CAPTURE_CONTENT", "") not in ("", "0", "false")


def emit_spans(root: SpanData, tracer: Any) -> None:
    """Emit a SpanData tree via an OTel tracer, preserving parent/child nesting."""
    from opentelemetry.trace import SpanKind

    kind_map = {
        "SERVER": SpanKind.SERVER,
        "INTERNAL": SpanKind.INTERNAL,
        "CLIENT": SpanKind.CLIENT,
    }

    def _emit(node: SpanData) -> None:
        with tracer.start_as_current_span(
            node.name, kind=kind_map.get(node.kind, SpanKind.INTERNAL)
        ) as span:
            for k, v in node.attributes.items():
                span.set_attribute(k, v)
            for child in node.children:
                _emit(child)

    _emit(root)


def export_run(
    trace: Trace,
    result: Optional[BenchmarkResult] = None,
    *,
    tracer: Any = None,
    **converter_kwargs: Any,
) -> Optional[SpanData]:
    """Convert a run to spans and (if OTel is available) emit them.

    Returns the SpanData root (always, for inspection); emission is a no-op when
    the ``otel`` extra is absent and no explicit tracer is supplied.
    """
    root = trace_to_spans(
        trace, result, capture_content=_content_capture_enabled(), **converter_kwargs
    )
    if tracer is not None:
        emit_spans(root, tracer)
        return root
    if not OTEL_AVAILABLE:
        return root  # no-op export; converter output still returned
    # Default provider → configured OTLP endpoint (Langfuse by default).
    provider = _ot_trace.get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        provider = TracerProvider()
        _ot_trace.set_tracer_provider(provider)
    emit_spans(root, _ot_trace.get_tracer("aobench"))
    return root
