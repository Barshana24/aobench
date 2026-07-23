# Marconi100 Node-Down Runbook

## Detecting an unreachable node
- A live node emits IPMI telemetry continuously (cadence ~minutes).
- A node with NO recent telemetry while peers keep reporting is likely down.
- Cross-check the SLURM node state: 'down' / 'drain' confirms it.

## Response
1. Query telemetry per node; find the node with no samples after some T0.
2. Confirm with `sinfo -N` / SLURM node state.
3. Reschedule affected jobs off the node.
4. Power-cycle via BMC (`ipmitool -H <bmc> power cycle`); check the IB link.
