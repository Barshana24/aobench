"""OTel-GenAI trace exporter (spec-0005, Feature 23, ADR 0003).

Emits AOBench runs as OpenTelemetry GenAI spans (``gen_ai.*``) with an
``aobench.*`` extension namespace, over OTLP. Langfuse-native; Phoenix/Datadog
work for free. Ships behind ``aobench[otel]``; no-ops when the extra is absent.
"""

from __future__ import annotations

from aobench.exporters.otel.converter import SpanData, trace_to_spans
from aobench.exporters.otel.exporter import OTEL_AVAILABLE, emit_spans, export_run

__all__ = ["trace_to_spans", "export_run", "emit_spans", "SpanData", "OTEL_AVAILABLE"]
