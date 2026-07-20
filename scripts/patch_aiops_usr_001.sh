#!/usr/bin/env bash
# patch_aiops_usr_001.sh — Run AIOPS_USR_001 for all Ollama dev models
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
    "qwen3.6:35b-a3b"
    "qwen3-coder-next:latest"
)

RUNS_ROOT="data/runs"
DEV_OLLAMA_DIR="${RUNS_ROOT}/v02_dev_ollama"
TASK="AIOPS_USR_001"
ENV="env_04"

export OLLAMA_BASE_URL="http://localhost:11434"
export LLM_PROVIDER="ollama"

for model in "${MODELS[@]}"; do
    existing_run=$(ls -d "${DEV_OLLAMA_DIR}/${model}/run_"* 2>/dev/null | tail -1)
    if [ -z "$existing_run" ]; then
        echo "SKIP $model: no dev run found"
        continue
    fi
    if [ -f "${existing_run}/results/${TASK}_result.json" ]; then
        echo "SKIP $model: already has ${TASK}"
        continue
    fi
    echo "Running ${TASK} for ${model}..."
    output=$(uv run aobench run task --task "${TASK}" --env "${ENV}" --adapter "openai:${model}" --output "${RUNS_ROOT}" --no-report 2>&1)
    run_id=$(echo "$output" | grep "Run ID:" | tail -1 | awk '{print $NF}')
    if [ -z "$run_id" ]; then
        echo "ERROR for $model: $output"
        continue
    fi
    cp "${RUNS_ROOT}/${run_id}/results/${TASK}_result.json" "${existing_run}/results/"
    rm -rf "${RUNS_ROOT}/${run_id}/"
    echo "  Done: $(echo "$output" | grep "aggregate_score")"
done
echo "All done."
