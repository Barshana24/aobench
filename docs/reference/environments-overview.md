# Environment Bundles — Overview

AOBench ships **26 deterministic HPC environment snapshot bundles**
under `benchmark/environments/env_01/` … `env_26/`, plus **six M100
ExaData-grounded bundles** (`env_m100_01` … `env_m100_06`, documented in
their own section below). Each bundle freezes a realistic operational
scenario — a job failure, a queue-congestion event, a cooling unit fault, a
policy violation, a multi-job interference incident, and so on — so that any
agent run against the bundle is reproducible.

This page is the cross-reference index: scenario type, scored roles, scored
QCATs, and the human description for each bundle. For the snapshot file
format (`slurm_state.json`, `telemetry/*.parquet`, `rbac_policy.yaml`,
`docs/*.md`, `incident_metadata.json`), see
[`environments.md`](../framework/environments.md). For the
authoritative `metadata.yaml` of each bundle, read the file directly.

---

## Scenario coverage at a glance

| Scenario type | Bundles | Headline |
|---------------|---------|----------|
| `job_failure` | env_01, env_17, env_18 | OOM kill, MPI timeout, missing checkpoint |
| `queue_congestion` | env_02, env_12 | Pending-queue spike, fairshare starvation |
| `thermal_power` | env_03 | Thermal-power monitoring snapshot |
| `rack_energy` | env_04 | Rack-level energy comparison |
| `cooling_failure` | env_05 | CRAC unit failure |
| `energy_anomaly` | env_06, env_07, env_19 | GPU power spike, PUE degradation, GPU idle waste |
| `node_degradation` | env_08, env_09 | Thermal throttling, ECC errors / flapping node |
| `policy_violation` | env_10, env_11 | Restricted-partition submit, allocation overrun |
| `capacity_planning` | env_13, env_14 | 6-month CPU trend, GPU demand forecast |
| `multi_job_interference` | env_15, env_20 | Memory oversubscription, Lustre I/O contention |
| `scheduler_misconfiguration` | env_16 | Wrong default partition after reconfig |
| `storage_management` | env_21 | Lustre quota pressure; per-user and per-project usage |
| `facility_incident` | env_22 | Cooling alarm response; degraded CRAC in high-density GPU row |
| `architecture_review` | env_23 | Capacity expansion planning; cluster topology and hardware inventory |

---

## All 23 bundles

| Env | Scenario type | Scored roles | Scored QCATs | Description |
|-----|---------------|--------------|--------------|-------------|
| **env_01** | `job_failure` | scientific_user, sysadmin | JOB, MON | User-job OOM failure on a memory-constrained node. |
| **env_02** | `queue_congestion` | sysadmin | JOB, MON | Pending-job queue is backed up and a sysadmin must triage. |
| **env_03** | `thermal_power` | facility_admin | MON, ENERGY | Thermal-power monitoring snapshot. |
| **env_04** | `rack_energy` | facility_admin | ENERGY, MON | Rack-by-rack energy comparison for cluster-wide review. |
| **env_05** | `cooling_failure` | facility_admin, sysadmin | ENERGY, MON | CRAC unit failure causing inlet-temperature anomalies. |
| **env_06** | `energy_anomaly` | sysadmin, facility_admin | ENERGY, MON | `gpu01` power draw spikes to 650 W (baseline ≈ 380 W) during a large training run. |
| **env_07** | `energy_anomaly` | facility_admin | ENERGY | Cluster PUE has degraded from 1.35 to 1.62 over 48 h due to a partial cooling fault. |
| **env_08** | `node_degradation` | sysadmin | MON, JOB | `node03` is thermally throttling because of a blocked cooling duct. |
| **env_09** | `node_degradation` | sysadmin | MON, JOB | `node06` is flapping between `allocated` and `draining` due to recurring ECC errors. |
| **env_10** | `policy_violation` | scientific_user, sysadmin | JOB | User `eve` submitted to the `restricted` partition without approval; SLURM held the job. |
| **env_11** | `policy_violation` | sysadmin, facility_admin | JOB, ENERGY | Account `ml-lab` has consumed 98 % of its monthly CPU-hour allocation. |
| **env_12** | `queue_congestion` | sysadmin | JOB | `ml-lab` has monopolised the cluster for 72 h, causing fairshare starvation and priority inversion. |
| **env_13** | `capacity_planning` | facility_admin, system_designer | MON, ENERGY | Six-month CPU-utilisation telemetry showing a steady upward trend. |
| **env_14** | `capacity_planning` | system_designer | ENERGY, MON | GPU partition utilisation has averaged 97 % for 30 days — demand-forecast input. |
| **env_15** | `multi_job_interference` | sysadmin, researcher | JOB, MON | Two jobs share `node01` (180 GB + 200 GB on a 256 GB node); swap activity is degrading both. |
| **env_16** | `scheduler_misconfiguration` | sysadmin | JOB | After a SLURM reconfig, the default partition was set incorrectly and is misrouting jobs. |
| **env_17** | `job_failure` | sysadmin | JOB, MON | A 4-node MPI job died after 6 h with exit 137 — suspected network-fault-induced SIGKILL. |
| **env_18** | `job_failure` | scientific_user | JOB | User `alice` resubmitted a long-running simulation but the checkpoint file is missing. |
| **env_19** | `energy_anomaly` | facility_admin | ENERGY | `gpu02` and `gpu03` allocated for 9 h but utilisation is ≈ 0 % — energy waste. |
| **env_20** | `multi_job_interference` | sysadmin | JOB, MON | Lustre I/O contention: a checkpoint job on nodes 1–4 is starving a science job on nodes 5–8. |
| **env_21** | `storage_management` | scientific_user, sysadmin, researcher, facility_admin, system_designer | DATA | Lustre quota pressure with per-user and per-project usage data; I/O metrics stub. |
| **env_22** | `facility_incident` | scientific_user, sysadmin, researcher, facility_admin, system_designer | FAC, ENERGY, DOCS | Cooling alarm response: CRAC-07 degraded in high-density GPU row C; BMS alarms and runbook. |
| **env_23** | `architecture_review` | sysadmin, researcher, facility_admin, system_designer | ARCH, PERF, DOCS | Capacity expansion planning: cluster topology, hardware inventory, and capacity planning guide. |

---

## M100 ExaData-grounded bundles

A separate set of six bundles grounded in the real CINECA Marconi100 (M100) ExaData
dataset. Telemetry uses real M100 metric vocabulary (`r{rack}n{slot}` nodes, IPMI/ganglia/
vertiv metric names) and values sampled from real M100 distributions — or real per-node traces
in `--real-baselines` mode — with a controlled, labeled perturbation per scenario. All six pass
the full F1–F7 fidelity gate.

| Env | Scenario | Scored roles | Headline |
|-----|----------|--------------|----------|
| **env_m100_01** | GPU thermal hotspot | sysadmin, scientific_user | `gpu3_core_temp` on r3n7 crosses the 84 °C throttle threshold while rack-3 peers stay normal. |
| **env_m100_02** | node power anomaly | sysadmin, facility_admin | `total_power` on r10n4 sustained above the 1300 W per-node alert vs its rack-10 peers. |
| **env_m100_03** | rack cooling fault | facility_admin | vertiv CRAC supply-air rise drives `ambient` up across all rack-4 nodes (28 °C warn → 32 °C crit). |
| **env_m100_04** | node down | sysadmin | r7n2 telemetry stops mid-window while peers keep reporting; SLURM marks it `down`. |
| **env_m100_05** | job↔telemetry failure | scientific_user | FAILED job 7798450 on r2n5; `total_power` collapses to idle at termination. |
| **env_m100_06** | real OOM | scientific_user | Real ExaData `OUT_OF_MEMORY` job 66353 on r5n3; ganglia `mem_free` exhaustion + power drop. |

Rebuild with `scripts/build_m100_bundles.py` (deterministic; `--real-baselines` for real per-node
traces, `--relative-anomalies` to scale anomalies to each node's real load). A gold-consistency
guard runs at the end of the build. See the
[M100 environments guide](../guides/m100_environments.md) for details.

---

## Per-bundle file layout

Every bundle has the same shape (some optional files appear only when
relevant to the scenario):

```
benchmark/environments/env_NN/
├── metadata.yaml                       Bundle metadata (env_id, scenario_type,
│                                       supported_roles, supported_categories,
│                                       included_sources)
├── manifest.txt                        Sorted list of all included files
├── slurm/
│   ├── slurm_state.json                Nodes, partitions, jobs (validated by SlurmState)
│   └── job_details.json                sacct-level details (when relevant)
├── telemetry/
│   ├── telemetry_timeseries.parquet    columns: timestamp, node_id, metric_name, value, unit
│   └── memory_events.csv               OOM / memory events (when relevant)
├── policy/
│   └── rbac_policy.yaml                Per-role permissions (schema v1.1)
├── docs/
│   ├── *.md                            User-facing knowledge documents
│   └── rbac_policy.md                  Auto-generated readable policy summary
└── incidents/
    └── incident_metadata.json          Incident timeline + affected resources
```

The `metadata.yaml` of every bundle is the authoritative source for what is
in scope. To list every file `manifest.txt` records:

```bash
cat benchmark/environments/env_05/manifest.txt
```

---

## Validating a bundle

`aobench validate benchmark` runs `validate_bundle()` from
`src/aobench/environment/snapshot_validator.py` over every bundle. It
checks JSON-schema conformance for `slurm_state.json`,
`incident_metadata.json`, and `rbac_policy.yaml`, plus the parquet column
schema for `telemetry/*.parquet`.

To regenerate a bundle (for example after editing the source CSVs):

```bash
python scripts/generate_bundles.py --env env_NN
```

`scripts/generate_bundles.py` also emits the auto-generated
`docs/rbac_policy.md` per environment from the YAML policy.
