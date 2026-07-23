# Marconi100 Job Failure Correlation Runbook

## Signals
- SLURM `job_state` = FAILED with an `exit_code` / `state_reason`.
- IPMI `total_power` and CPU package power (`p0_power`, `p1_power`) drop to
  near-idle on the job's node at the failure time as the process terminates.

## Correlating a failure
1. Find the failed job and its node + end_time via SLURM.
2. Query telemetry for that node around end_time.
3. A power collapse aligned with end_time confirms the workload died there
   (vs a node hardware fault, where idle power would be abnormal).
