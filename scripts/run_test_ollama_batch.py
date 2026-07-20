"""run_test_ollama_batch.py — Run all 13 Ollama models on the held-out test split.

Opens the SSH tunnel (same credentials as run_ollama_batch.py), checks which
models already have complete runs under data/runs/v02_test_ollama/, then runs
each pending model in sequence smallest-first.

IMPORTANT: requires AOBENCH_UNLOCK_TEST=1 to access the test split.  This is
set automatically within this script — do NOT set it globally in .env.

Usage:
    uv run python scripts/run_test_ollama_batch.py [--dry-run]
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ollama_tunnel import open_tunnel  # noqa: E402

# ── Config ─────────────────────────────────────────────────────────────────────

OUTPUT_DIR = "data/runs/v02_test_ollama"
SPLIT      = "test"
MIN_RESULTS = 16   # test split = 18 tasks; ≤2 failures tolerated

# Same model order as dev batch (smallest → largest)
MODELS: list[tuple[str, str | None]] = [
    ("mistral-nemo:latest",     None),   # 7.1 GB
    ("gemma4:e4b",              None),   # 9.6 GB
    ("gpt-oss:latest",          None),   # 13.8 GB
    ("gpt-oss:20b",             None),   # 13.8 GB
    ("devstral-small-2:24b",    None),   # 15.2 GB
    ("mistral-small:24b",       None),   # 14.3 GB
    ("GLM-4.7-Flash:latest",    None),   # 19.0 GB
    ("gemma4:31b",              None),   # 19.9 GB
    ("qwen3.6:35b-a3b",         None),   # 23.9 GB
    ("nemotron3:33b",           None),   # 27.6 GB
    ("qwen3-coder-next:latest", None),   # 51.7 GB
    ("qwen3.5:122b",            None),   # 81.4 GB
    ("nemotron-3-super:latest", None),   # 86.8 GB
]


def count_results(model: str) -> int:
    model_dir = Path(OUTPUT_DIR) / model
    if not model_dir.exists():
        return 0
    return len(list(model_dir.rglob("*_result.json")))


def run_model(model: str, dry_run: bool = False) -> int:
    env = os.environ.copy()
    env["OLLAMA_BASE_URL"]      = "http://localhost:11434"
    env["LLM_PROVIDER"]         = "ollama"
    env["AOBENCH_UNLOCK_TEST"]  = "1"

    cmd = [
        "uv", "run", "aobench", "run", "all",
        "--split", SPLIT,
        "--models", model,
        "--output", OUTPUT_DIR,
        "--langfuse",
    ]
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Running: {' '.join(cmd)}", flush=True)
    if dry_run:
        return 0
    result = subprocess.run(cmd, env=env)
    return result.returncode


def wait_for_ollama(port: int = 11434, timeout: int = 10) -> bool:
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://localhost:{port}/api/tags", timeout=3) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    print("[batch-test] Opening SSH tunnel …", flush=True)
    ssh, server_sock, stop_event = open_tunnel()
    time.sleep(1.0)

    if not wait_for_ollama():
        print("[batch-test] ERROR: Ollama not reachable.", file=sys.stderr)
        stop_event.set(); server_sock.close(); ssh.close()
        sys.exit(1)
    print("[batch-test] Tunnel ready. Starting test-split runs.", flush=True)

    summary: list[dict] = []

    try:
        for model, skip_reason in MODELS:
            if skip_reason:
                print(f"\n[batch-test] SKIP {model}: {skip_reason}", flush=True)
                continue

            n = count_results(model)
            if n >= MIN_RESULTS:
                print(f"\n[batch-test] SKIP {model}: already complete ({n} results)", flush=True)
                summary.append({"model": model, "status": "skipped", "results": n})
                continue

            if n > 0:
                print(f"\n[batch-test] {model}: {n} results — re-running", flush=True)
            else:
                print(f"\n[batch-test] {model}: fresh run", flush=True)

            rc = run_model(model, dry_run=dry_run)
            status = "ok" if rc == 0 else f"error(rc={rc})"
            summary.append({"model": model, "status": status, "results": count_results(model)})
            print(f"[batch-test] {model} → {status}", flush=True)

    finally:
        stop_event.set()
        server_sock.close()
        ssh.close()

    print("\n\n=== Test-split batch summary ===")
    for r in summary:
        print(f"  {r['model']:40s}  {r['status']}  ({r['results']} results)")


if __name__ == "__main__":
    main()
