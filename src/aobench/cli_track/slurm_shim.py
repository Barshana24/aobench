"""Mock Slurm CLI core logic (Feature 20).

The terminal track bakes thin ``sbatch``/``squeue``/``scontrol``/``sacct`` shim
executables into the env container; each shim just calls into this pure
interpreter, which reads/writes the same ``slurm_state.json`` structure the mock
``SlurmTool`` uses — so a real ``squeue`` command and the mock tool return the
*same* ground truth (ADR 0004 §2, ADR 0006).

State shape (subset)::

    {"jobs": [
        {"job_id": "101", "user": "alice", "name": "train", "state": "RUNNING",
         "partition": "gpu", "nodes": "node01", "time": "01:00:00"},
        ...
    ]}
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class ShimResult(BaseModel):
    stdout: str
    exit_code: int = 0


def _jobs(state: dict[str, Any]) -> list[dict[str, Any]]:
    return list(state.get("jobs", []))


def _squeue(argv: list[str], state: dict[str, Any]) -> ShimResult:
    jobs = _jobs(state)
    user: Optional[str] = None
    job_id: Optional[str] = None
    i = 0
    while i < len(argv):
        if argv[i] in ("-u", "--user") and i + 1 < len(argv):
            user = argv[i + 1]
            i += 2
            continue
        if argv[i] in ("-j", "--job") and i + 1 < len(argv):
            job_id = argv[i + 1]
            i += 2
            continue
        i += 1
    if user is not None:
        jobs = [j for j in jobs if j.get("user") == user]
    if job_id is not None:
        jobs = [j for j in jobs if str(j.get("job_id")) == job_id]

    header = "JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST"
    lines = [header]
    for j in jobs:
        lines.append(
            f"{j.get('job_id',''):>5} {j.get('partition',''):>9} "
            f"{j.get('name',''):>8} {j.get('user',''):>8} "
            f"{_st(j.get('state','')):>2} {j.get('time',''):>10} "
            f"{1:>6} {j.get('nodes','')}"
        )
    return ShimResult(stdout="\n".join(lines), exit_code=0)


def _st(state: str) -> str:
    return {"RUNNING": "R", "PENDING": "PD", "COMPLETED": "CD", "FAILED": "F"}.get(state, state[:2])


def _scontrol(argv: list[str], state: dict[str, Any]) -> ShimResult:
    # scontrol show job <id>
    if len(argv) >= 3 and argv[0] == "show" and argv[1] == "job":
        jid = argv[2]
        for j in _jobs(state):
            if str(j.get("job_id")) == jid:
                fields = " ".join(f"{k}={v}" for k, v in j.items())
                return ShimResult(stdout=f"JobId={jid} {fields}", exit_code=0)
        return ShimResult(stdout=f"slurm_load_jobs error: Invalid job id {jid}", exit_code=1)
    return ShimResult(stdout="scontrol: unsupported subcommand", exit_code=1)


def _sacct(argv: list[str], state: dict[str, Any]) -> ShimResult:
    job_id: Optional[str] = None
    i = 0
    while i < len(argv):
        if argv[i] in ("-j", "--jobs") and i + 1 < len(argv):
            job_id = argv[i + 1]
            i += 2
            continue
        i += 1
    jobs = _jobs(state)
    if job_id is not None:
        jobs = [j for j in jobs if str(j.get("job_id")) == job_id]
    lines = ["JobID    JobName  State     ExitCode"]
    for j in jobs:
        lines.append(
            f"{j.get('job_id',''):>7} {j.get('name',''):>8} "
            f"{j.get('state',''):>9} {j.get('exit_code','0:0'):>8}"
        )
    return ShimResult(stdout="\n".join(lines), exit_code=0)


def _sbatch(argv: list[str], state: dict[str, Any]) -> ShimResult:
    # Assign next id and append a PENDING job (mutates state in place).
    existing = [int(j["job_id"]) for j in _jobs(state) if str(j.get("job_id")).isdigit()]
    new_id = (max(existing) + 1) if existing else 1000
    script = argv[-1] if argv else "batch"
    state.setdefault("jobs", []).append({
        "job_id": str(new_id), "user": state.get("current_user", "user"),
        "name": script, "state": "PENDING", "partition": "normal",
        "nodes": "", "time": "0:00",
    })
    return ShimResult(stdout=f"Submitted batch job {new_id}", exit_code=0)


_DISPATCH = {"squeue": _squeue, "scontrol": _scontrol, "sacct": _sacct, "sbatch": _sbatch}


def run_slurm_command(argv: list[str], state: dict[str, Any]) -> ShimResult:
    """Interpret ``argv`` (e.g. ``["squeue", "-u", "alice"]``) against ``state``."""
    if not argv:
        return ShimResult(stdout="", exit_code=1)
    cmd, rest = argv[0], argv[1:]
    handler = _DISPATCH.get(cmd)
    if handler is None:
        return ShimResult(stdout=f"{cmd}: command not found", exit_code=127)
    return handler(rest, state)
