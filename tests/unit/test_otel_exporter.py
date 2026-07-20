"""Tests for the OTel-GenAI trace exporter (spec-0005)."""

from __future__ import annotations

import pytest

from aobench.exporters.otel import semconv as sc
from aobench.exporters.otel import export_run, trace_to_spans
from aobench.exporters.otel.exporter import OTEL_AVAILABLE
from aobench.schemas.result import BenchmarkResult, DimensionScores
from aobench.schemas.trace import ToolCall, Trace, TraceStep


def _trace(hard_fail: bool = False) -> Trace:
    return Trace(
        trace_id="trace_x",
        run_id="run_x",
        task_id="JOB_USR_001",
        role="hpc_user",
        environment_id="env_01",
        adapter_name="openai:gpt-4o",
        model_name="gpt-4o",
        prompt_tokens=100,
        completion_tokens=40,
        final_answer="the answer",
        hard_fail=hard_fail,
        steps=[
            TraceStep(step_id=1, step_type="reasoning", reasoning="think"),
            TraceStep(
                step_id=2, step_type="tool_call", span_id="trace_x_step_002",
                tool_call=ToolCall(tool_name="SlurmTool", method="query_jobs"),
            ),
        ],
    )


def _result(hard_fail: bool = False) -> BenchmarkResult:
    from datetime import datetime, timezone

    return BenchmarkResult(
        result_id="res_x", run_id="run_x", task_id="JOB_USR_001", role="hpc_user",
        environment_id="env_01", adapter_name="openai:gpt-4o", hard_fail=hard_fail,
        dimension_scores=DimensionScores(outcome=0.8, tool_use=0.6, governance=1.0),
        aggregate_score=0.75, task_category="JOB",
        cost_estimate_usd=0.01, timestamp=datetime.now(tz=timezone.utc),
    )


# AC1 — span tree + attributes
def test_span_tree_shape_and_attrs():
    root = trace_to_spans(_trace(), _result(), env_manifest_sha256="abc123", split="dev")
    assert root.name == sc.ROOT_SPAN
    assert root.kind == sc.KIND_SERVER
    assert root.attributes[sc.CONVERSATION_ID] == "run_x"
    assert root.attributes[sc.AO_TASK_ID] == "JOB_USR_001"
    assert root.attributes[sc.AO_ENV_MANIFEST_SHA] == "abc123"
    assert root.attributes[sc.AO_SEMCONV_VERSION] == sc.SEMCONV_VERSION

    names = [s.name for s in root.walk()]
    assert any(n.startswith("invoke_agent") for n in names)
    assert any(n.startswith("chat") for n in names)
    assert any(n.startswith("execute_tool SlurmTool") for n in names)
    assert sc.SCORE_SPAN in names

    # score attributes propagate to root
    assert root.attributes[sc.score_attr("outcome")] == 0.8
    # chat span carries token usage
    chat = next(s for s in root.walk() if s.name.startswith("chat"))
    assert chat.attributes[sc.USAGE_INPUT_TOKENS] == 100
    assert chat.attributes[sc.USAGE_OUTPUT_TOKENS] == 40
    assert chat.attributes[sc.REQUEST_MODEL] == "gpt-4o"
    # provider inferred
    assert chat.attributes[sc.PROVIDER_NAME] == "openai"


# AC2 — content NOT captured by default
def test_content_not_captured_by_default():
    root = trace_to_spans(_trace(), _result(), capture_content=False)
    for s in root.walk():
        assert sc.INPUT_MESSAGES not in s.attributes
        assert sc.OUTPUT_MESSAGES not in s.attributes


def test_content_captured_when_enabled():
    root = trace_to_spans(_trace(), _result(), capture_content=True)
    texts = [s.attributes for s in root.walk()]
    assert any(sc.OUTPUT_MESSAGES in a for a in texts)


# AC3 — governance hard-fail flag
def test_hard_fail_flag():
    root = trace_to_spans(_trace(hard_fail=True), _result(hard_fail=True))
    assert root.attributes[sc.AO_GOVERNANCE_HARD_FAIL] is True


# AC4 — export no-op / return when tracer path
def test_export_run_returns_root_without_tracer():
    root = export_run(_trace(), _result())
    assert root is not None
    assert root.name == sc.ROOT_SPAN


# Real OTLP emission via in-memory exporter (spec-0005 test plan)
def test_emit_via_inmemory_span_exporter():
    if not OTEL_AVAILABLE:
        pytest.skip("otel extra not installed")
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    provider = TracerProvider()
    mem = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(mem))
    tracer = provider.get_tracer("aobench-test")

    export_run(_trace(), _result(), tracer=tracer)
    spans = mem.get_finished_spans()
    names = {s.name for s in spans}
    assert sc.ROOT_SPAN in names
    assert sc.SCORE_SPAN in names
    assert any(n.startswith("execute_tool") for n in names)
    root_span = next(s for s in spans if s.name == sc.ROOT_SPAN)
    assert root_span.attributes[sc.CONVERSATION_ID] == "run_x"
