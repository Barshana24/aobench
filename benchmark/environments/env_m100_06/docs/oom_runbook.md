# Marconi100 Out-Of-Memory (OOM) Runbook

## Signals
- SLURM `job_state` = OUT_OF_MEMORY (the scheduler's own classification).
- ganglia `mem_free` on the node approaches 0 (against `mem_total`) just before the kill.
- `total_power` / CPU package power drop to idle when the process dies.

## Diagnosis
1. Confirm the job's `job_state` is OUT_OF_MEMORY via SLURM.
2. Query telemetry `mem_free` for the node around the failure time — a fall toward 0
   confirms memory exhaustion (vs a node hardware fault).
3. Distinguish from a hardware fault: after an OOM kill idle power is normal.

## Remediation (user)
- Reduce per-task memory footprint or batch size.
- Request more memory (`--mem`) or a high-memory node.
- Use fewer tasks per node so each gets more RAM.
