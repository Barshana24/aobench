"""OTel-GenAI semantic-convention attribute names + AOBench extensions.

The GenAI semconv is experimental (as of 2026); pinning every attribute name in
this single module means a convention bump is a one-file change (spec-0005 R5).
"""

from __future__ import annotations

SEMCONV_VERSION = "gen_ai-1.29-experimental"

# --- Standard OTel GenAI attributes ---
OP_NAME = "gen_ai.operation.name"
PROVIDER_NAME = "gen_ai.provider.name"
REQUEST_MODEL = "gen_ai.request.model"
RESPONSE_MODEL = "gen_ai.response.model"
RESPONSE_ID = "gen_ai.response.id"
FINISH_REASONS = "gen_ai.response.finish_reasons"
USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
AGENT_NAME = "gen_ai.agent.name"
AGENT_ID = "gen_ai.agent.id"
TOOL_NAME = "gen_ai.tool.name"
TOOL_CALL_ID = "gen_ai.tool.call.id"
CONVERSATION_ID = "gen_ai.conversation.id"
INPUT_MESSAGES = "gen_ai.input.messages"
OUTPUT_MESSAGES = "gen_ai.output.messages"
SYSTEM_INSTRUCTIONS = "gen_ai.system_instructions"

# --- Operation-name values ---
OP_INVOKE_AGENT = "invoke_agent"
OP_CHAT = "chat"
OP_EXECUTE_TOOL = "execute_tool"

# --- AOBench extension namespace ---
AO_TASK_ID = "aobench.task.id"
AO_QCAT = "aobench.qcat"
AO_ROLE = "aobench.role"
AO_ENV_ID = "aobench.env.id"
AO_ENV_MANIFEST_SHA = "aobench.env.manifest_sha256"
AO_SPLIT = "aobench.split"
AO_SCORING_MODE = "aobench.scoring_mode"
AO_GOVERNANCE_HARD_FAIL = "aobench.governance.hard_fail"
AO_REPLAY_SEED = "aobench.replay.seed"
AO_REPLAY_MODE = "aobench.replay.mode"
AO_COST_USD = "aobench.cost.usd"
AO_ENERGY_KWH = "aobench.energy.kwh"
AO_CO2E_G = "aobench.co2e.g"
AO_SEMCONV_VERSION = "aobench.semconv.version"


def score_attr(dimension: str) -> str:
    """Attribute name for a per-dimension score, e.g. aobench.score.outcome."""
    return f"aobench.score.{dimension}"


def cfs_attr(component: str) -> str:
    """Attribute name for a Cascading-Failure-Score component."""
    return f"aobench.cfs.{component}"


# --- Span names / kinds ---
ROOT_SPAN = "aobench.task_run"
SCORE_SPAN = "aobench.score"

KIND_SERVER = "SERVER"
KIND_INTERNAL = "INTERNAL"
KIND_CLIENT = "CLIENT"
