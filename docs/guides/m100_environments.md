# M100-grounded environments

AOBench ships a set of environment bundles (`env_m100_*`) and tasks (`M100_*`) that are
**grounded in the real CINECA Marconi100 (M100) "ExaData" dataset** rather than purely
synthetic data. They use M100's real metric vocabulary and node naming, with telemetry
values sampled from real M100 distributions, plus a controlled labeled fault per scenario.

These run alongside the original `env_01…` environments — nothing about the existing
benchmark changes.

## What's M100-faithful

- **Node names** follow M100's `r{rack}n{slot}` convention (e.g. `r3n7`, `r10n4`).
- **Metric names** are the real IPMI metrics: `total_power`, `ambient`,
  `gpu0/1/3/4_core_temp` (M100 nodes have no GPU 2), `gpuN_mem_temp`, `fanX_Y`,
  `psN_input_power`, `pN_power`, …
- **Telemetry** is stored in the canonical long-format parquet with the usual columns
  (`timestamp, node_id, metric_name, value, unit`) plus an extra `plugin` column
  (`ipmi_pub`) for provenance.
- **Distributions** (baseline level, fast noise, slow drift, clamp bounds, **cross-node
  baseline spread**) are fit from a **population of 120 real M100 nodes** — so daily
  patterns, noise, and node-to-node variation look like real Marconi100 operation. Each env
  node is given its own real baseline drawn from the measured population spread.

## Available environments

| Env | Scenario | Key metrics | Roles |
|---|---|---|---|
| `env_m100_01` | GPU thermal hotspot — `r3n7` GPU3 ramps to ~88°C | `gpu3_core_temp`, `fanX_Y` | sysadmin, scientific_user |
| `env_m100_02` | Node power anomaly — `r10n4` ~1400W vs ~644W baseline | `total_power`, `psN_input_power` | sysadmin, facility_admin |
| `env_m100_03` | Rack cooling fault — rack-4 `ambient` rises to ~32°C on all nodes | `ambient` | facility_admin, sysadmin |
| `env_m100_04` | Node down — `r7n2` telemetry stops ~10:45 UTC | (telemetry gap) + SLURM `down` | sysadmin, scientific_user |
| `env_m100_05` | Job failure correlation — `r2n5` power collapse at FAILED time | `total_power`, `pN_power` | scientific_user, sysadmin |
| `env_m100_06` | **Real OOM** — real `OUT_OF_MEMORY` job + real `mem_free` exhaustion on `r5n3` | `mem_free`, `mem_total`, `total_power` | scientific_user, sysadmin |

Associated tasks (all **dev** split): `M100_MON_SYS_001/002`, `M100_MON_USR_001`,
`M100_ENERGY_SYS_001`, `M100_ENERGY_FAC_001/002`, `M100_JOB_USR_001/002`.

`env_m100_06` is anchored on an **actual** Marconi100 `OUT_OF_MEMORY` job record (job 66353)
from the ExaData `job_table`, with memory telemetry (`mem_free`/`mem_total`) fit from the real
`ganglia_pub` plugin — the closest to fully-real grounding in the suite.

## Running one

```bash
uv run aobench run task --task M100_MON_SYS_001 --env env_m100_01 --adapter direct_qa
```

## Regenerating the bundles

The bundles are reproducible from repo contents alone (no large download needed):

```bash
# Phase 1 — rebuild the env_m100_* bundles (deterministic; seeded per env).
# Uses the committed population reference, so this works offline on any machine.
uv run python scripts/build_m100_bundles.py
```

The committed reference (`benchmark/environments/_m100_reference/metric_distributions.json`)
was fit across 120 real nodes from the full ExaData `time_aggregated/` dataset.

**You do not need the full dataset** — the reference above is committed, so bundle building
works offline. Refreshing it is only necessary if you want to re-fit against the raw data
yourself, which requires obtaining the
[M100 ExaData dataset](https://doi.org/10.5281/zenodo.7541722) (see
[Source and citation](#source-and-citation)) and setting
`EXADATA_DIR` to wherever you extracted it:

```bash
export EXADATA_DIR=/path/to/your/exadata

# Over a population of real nodes:
uv run --with pandas --with pyarrow python scripts/build_m100_reference.py \
    --aggregated-dir $EXADATA_DIR/time_aggregated \
    --catalog $EXADATA_DIR/data_extraction/M100_metrics.csv \
    --out benchmark/environments/_m100_reference --n-nodes 120 --seed 388

# Offline fallback (no full dataset): fit from the single bundled node sample
uv run python scripts/build_m100_reference.py
```

## Real per-node baselines (advanced)

By default the env baselines are sampled from the real-node *population distributions*
(deterministic, builds offline, matches the gold answers). Where the full ExaData dataset is
available (the `n1` server), you can instead pull each env node's **actual real trace**:

```bash
uv run python scripts/build_m100_bundles.py \
    --real-baselines $EXADATA_DIR/time_aggregated
```

This gives genuinely real, heterogeneous peer telemetry. Add `--relative-anomalies` so the
injected anomalies scale to each node's real baseline and stay clearly separated from noisy real
peer load (e.g. the power spike becomes ~2.4× the busiest real peer).

**Real-baseline mode is now also scored.** The task gold answers are written in qualitative,
mode-invariant terms — they assert node identity, named-constant threshold crossings (e.g. the
84°C GPU throttle, the 1300W per-node power alert), peer relationships, and the recommended
action, rather than sampled absolute magnitudes. The same gold therefore scores correctly under
both the distribution-sampled build and the real-baseline build. Distribution-sampled stays the
**default** (deterministic, byte-identical, builds offline); real-baseline is an opt-in scored
variant for evaluating on real per-node traces.

At the end of the build a **gold-consistency guard** verifies that each env's generated telemetry
actually satisfies the qualitative facts its gold answer relies on (the anomaly node crosses its
named threshold, peers stay below it, a downed node drops out, a collapse occurs) — in both modes
— and fails the build otherwise, so a build can never silently de-sync from the scored gold. See
the [M100 ExaData dataset paper](https://doi.org/10.1038/s41597-023-02174-3) for details.

## Governance on the user tasks

The three `scientific_user` M100 tasks (`M100_MON_USR_001`, `M100_JOB_USR_001`,
`M100_JOB_USR_002`) carry `hard_fail_conditions` (e.g. `access_other_user_job`,
`disclose_system_topology`) naming the role-forbidden actions. An agent that over-reaches —
querying another user's jobs or disclosing topology — trips the env's RBAC enforcement and loses
governance credit, while a careful agent keeps it; the do-nothing baseline is discounted by the
engagement-aware CLEAR Assurance metric. The `sysadmin` and `facility_admin` tasks have no such
conditions (those roles legitimately drain nodes and control cooling).

## Real job records

Each env queue includes a few **real anonymized M100 job records** (drawn from a committed pool
of real `job_table` records — real partitions, QoS, CPU counts, walltimes, and genuine terminal
states including `OUT_OF_MEMORY`, `NODE_FAIL`, `TIMEOUT`) alongside the synthetic scenario jobs.
This is on by default and builds offline; pass `--no-real-jobs` to use only synthetic jobs. To
refresh the pool from a different month, extract `job_table` from a `raw/` tar on `n1` and run
`scripts/build_m100_jobs.py`.

## Provenance

Each environment includes a `provenance.json` recording the data source, RNG seed,
scenario, and the exact injected perturbation. The data originates from the CINECA
Marconi100 ExaData dataset.
For the design rationale (including how these bundles satisfy the F1–F7 fidelity gate),
see the M100 ExaData dataset paper below.

## Source and citation

The six `env_m100_*` bundles are derived from **M100 ExaData**, the public operational
dataset of CINECA's Marconi100 Tier-0 supercomputer — 980+ nodes, two and a half years of
management, workload, facility and infrastructure data, collected with the EXAMON
monitoring framework.

| | |
|---|---|
| **Dataset paper** | Borghesi et al., *M100 ExaData: a data collection campaign on the CINECA's Marconi100 Tier-0 supercomputer*, **Scientific Data** 10, 288 (2023) — [nature.com/articles/s41597-023-02174-3](https://www.nature.com/articles/s41597-023-02174-3) · [doi:10.1038/s41597-023-02174-3](https://doi.org/10.1038/s41597-023-02174-3) |
| **Data-access code** | [gitlab.com/ecs-lab/exadata](https://gitlab.com/ecs-lab/exadata) — the open-source modules for reading the dataset, plus the node-position documentation |
| **Dataset** | Published via Zenodo — [doi:10.5281/zenodo.7541722](https://doi.org/10.5281/zenodo.7541722) (49.9 TB uncompressed) |

**If you use the `env_m100_*` environments or the `M100_*` tasks in published work, cite
the dataset paper as well as AOBench.** The grounding is what makes those results a claim
about a real machine rather than about a simulator, and that grounding is someone else's
data-collection campaign. See [Cite AOBench](../about/citation.md) for both entries.
