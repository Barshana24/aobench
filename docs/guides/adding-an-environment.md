---
title: "Adding an environment snapshot bundle to AOBench"
description: "How to contribute a new HPC environment snapshot to AOBench: the bundle layout, metadata.yaml, telemetry and Slurm formats, RBAC policy, sanitisation requirements for real facility data, and validation."
keywords:
  - HPC snapshot bundle
  - contribute benchmark environment
  - sanitise cluster telemetry
---

# Adding an environment

An environment bundle is a frozen cluster: everything the mock tools read, at one
moment in time. It is what makes an AOBench result reproducible years later without
access to any machine.

!!! tip "The most valuable contribution in this project"
    A **sanitised snapshot from a real facility** is worth more than any amount of
    synthetic authoring. Twenty-three of AOBench's twenty-nine environments are
    invented; six come from real Marconi100 data, and those six are the ones that make
    the benchmark credible. If you operate a cluster and can publish a sanitised
    window, please [start a discussion](https://github.com/MSKazemi/aobench/discussions)
    — we will help with the format and the sanitisation review.

## Bundle layout

```
benchmark/environments/env_XX/
├── metadata.yaml              # required — identity and capability declaration
├── manifest.txt               # file inventory
├── slurm/
│   ├── slurm_state.json       # nodes, partitions, queue state
│   └── job_details.json       # per-job records
├── telemetry/
│   ├── telemetry_timeseries.parquet
│   └── *.csv                  # event streams (memory events, throttling, …)
├── docs/
│   └── *.md                   # site documentation the agent may consult
├── policy/
│   └── rbac_policy.yaml       # which roles may call which tools
├── incidents/
│   └── incident_metadata.json
└── provenance.json            # required for real-data bundles
```

Not every bundle needs every directory — `metadata.yaml` declares what is present in
`included_sources` and `included_files`, and the loader trusts that declaration.

## `metadata.yaml`

```yaml
environment_id: env_30
snapshot_name: Storage Saturation During Checkpoint Storm
scenario_type: filesystem_pressure
cluster_name: your-cluster
snapshot_timestamp: 2026-03-01T02:00:00Z
bundle_root: environments/env_30
supported_roles:
  - sysadmin
  - scientific_user
supported_categories:
  - DATA
  - PERF
included_sources: [slurm, telemetry, docs, rbac]
included_files:
  - slurm/slurm_state.json
  - telemetry/telemetry_timeseries.parquet
  - policy/rbac_policy.yaml
  - docs/storage_runbook.md
implementation_status: bundled
validation_status: validated
description: >-
  One sentence a reader can understand without opening any file. What is
  happening on this machine, and what should an operator be able to work out?
```

`description` earns its keep: it is what appears in the
[environment catalog](../reference/environment-catalog.md) and what a contributor reads
when deciding whether their task idea fits your bundle.

## Design principles

**One scenario per bundle.** A bundle should have a single thing going on that an
operator could diagnose. Bundles with three unrelated anomalies make it impossible to
tell whether an agent found the right one.

**The evidence must be there.** Whatever a task will ask about must be visible in the
data. If the story is "GPU3 on r3n7 overheated", the telemetry must actually show
gpu3_core_temp climbing on r3n7, and peer nodes must actually look normal.

**Include distractors, but honest ones.** Real telemetry is noisy and real clusters
have several things slightly wrong at once. A bundle with exactly one non-nominal
signal is unrealistically easy.

**Documentation matters.** Site runbooks and policy docs are what turn a guessing task
into a grounded one. Write the doc a real site would have — including the parts that
are slightly out of date, if that is realistic.

## RBAC policy

Every bundle needs `policy/rbac_policy.yaml`, mapping roles to permitted tools. Be
honest about what each role may see: the governance dimension is only as meaningful as
this file.

Note the standing limitation — **every RBAC policy currently in the corpus is
synthetic**, including in the grounded bundles. A contribution of a realistic (even if
generalised) site authorisation model would materially improve the benchmark.

## Sanitising real facility data

If your bundle derives from a real cluster, this section is the important one. HPC
operational data leaks identity in more places than people expect:

- [ ] **Usernames and UIDs** — replace consistently; do not just truncate
- [ ] **Project and allocation names** — these identify research groups
- [ ] **Job names and script paths** — routinely contain a person's name or a paper title
- [ ] **Hostnames** — may reveal site topology; generalise if that is a concern
- [ ] **Documentation** — internal runbooks contain contact names and phone numbers
- [ ] **Incident text** — free-text incident notes are the highest-risk field
- [ ] **Timestamps** — an exact timestamp plus a public outage notice can re-identify

**Sanitisation is the contributor's responsibility, and we will review it as if it were
not.** A maintainer will read every file in a real-data bundle before it merges. Get
your own institution's clearance first; we cannot give it to you.

Record what you did in `provenance.json`:

```json
{
  "source": "Public ExaData release, CINECA Marconi100",
  "source_url": "https://doi.org/...",
  "window": "2022-07-15T12:00:00Z/2022-07-15T16:00:00Z",
  "channels": ["gpu3_core_temp", "ambient_temp", "..."],
  "transformations": ["resampled to 60s", "node IDs generalised", "RBAC policy synthesised"],
  "sanitisation_review": "institution approval reference or 'public source, no PII'"
}
```

## Validate

```bash
aobench validate benchmark          # schema + fidelity gate
aobench list envs | grep env_30     # does it show up correctly?
make catalog                        # regenerate the catalog page
```

Then write at least one task against it — an environment with no tasks is dead weight,
and writing the task is how you find out whether the evidence is really there. See
[adding a task](adding-a-task.md).

## Review checklist

- [ ] `metadata.yaml` complete, `description` readable by a non-expert
- [ ] `aobench validate benchmark` passes
- [ ] One coherent scenario, with the evidence genuinely present
- [ ] Realistic distractors
- [ ] `rbac_policy.yaml` present and defensible
- [ ] For real data: sanitisation checklist completed, `provenance.json` filled in
- [ ] At least one task authored against it
- [ ] `make catalog` run and committed
