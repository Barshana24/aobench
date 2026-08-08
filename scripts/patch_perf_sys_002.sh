#!/usr/bin/env bash
# patch_perf_sys_002.sh — Run PERF_SYS_002 for Ollama models and merge
# the result into each model's existing test run directory.
# Must be run from the repository root.
set -euo pipefail

MODELS=(
    "devstral-small-2:24b"
    "gemma4:31b"
    "gemma4:e4b"
    "GLM-4.7-Flash:latest"
    "gpt-oss:20b"
    "gpt-oss:latest"
    "mistral-nemo:latest"
    "mistral-small:24b"
    "nemotron3:33b"
    "nemotron-3-super:latest"
    "qwen3.5:122b"
    "qwen3-coder-next:latest"
)

RUNS_ROOT="data/runs"
TEST_OLLAMA_DIR="${RUNS_ROOT}/v02_test_ollama"
TASK="PERF_SYS_002"
ENV="env_09"

export OLLAMA_BASE_URL="http://localhost:11434"
export LLM_PROVIDER="ollama"
export AOBENCH_UNLOCK_TEST=1

for model in "${MODELS[@]}"; do
    echo "========================================="
    echo "Running ${TASK} for model: ${model}"
    echo "========================================="

    # Find existing test run directory for this model
    existing_run=$(ls -d "${TEST_OLLAMA_DIR}/${model}/run_"* 2>/dev/null | tail -1)
    if [ -z "$existing_run" ]; then
        echo "ERROR: No existing test run found for ${model}, skipping"
        continue
    fi
    echo "Target run dir: ${existing_run}"

    # Check if result already exists
    if [ -f "${existing_run}/results/${TASK}_result.json" ]; then
        echo "SKIP: ${TASK}_result.json already exists in ${existing_run}"
        continue
    fi

    # Run the task (creates a new temp run directory in data/runs/)
    echo "Running aobench run task --task ${TASK} --env ${ENV} --adapter openai:${model} --no-report ..."
    TEMP_OUTPUT=$(uv run aobench run task \
        --task "${TASK}" \
        --env "${ENV}" \
        --adapter "openai:${model}" \
        --output "${RUNS_ROOT}" \
        --no-report \
        2>&1)
    echo "$TEMP_OUTPUT"

    # Extract the run_id from the output
    RUN_ID=$(echo "$TEMP_OUTPUT" | grep "Run ID:" | tail -1 | awk '{print $NF}')
    if [ -z "$RUN_ID" ]; then
        echo "ERROR: Could not extract Run ID from output for ${model}"
        continue
    fi
    echo "New run ID: ${RUN_ID}"

    TEMP_RUN_DIR="${RUNS_ROOT}/${RUN_ID}"
    RESULT_FILE="${TEMP_RUN_DIR}/results/${TASK}_result.json"

    if [ ! -f "$RESULT_FILE" ]; then
        echo "ERROR: Result file not found at ${RESULT_FILE}"
        continue
    fi

    # Copy result to existing test run directory
    cp "${RESULT_FILE}" "${existing_run}/results/${TASK}_result.json"
    echo "Copied result to: ${existing_run}/results/${TASK}_result.json"

    # Clean up temp run directory
    rm -rf "${TEMP_RUN_DIR}"
    echo "Cleaned up temp run dir: ${TEMP_RUN_DIR}"
    echo ""
done

echo "Done! All models processed."
