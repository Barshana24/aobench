---
title: "Datasheet for the AOBench corpus"
description: "Datasheets-for-Datasets record for the AOBench benchmark corpus: motivation, composition, collection process, preprocessing, uses, distribution, and maintenance of the 88 tasks and 29 environment snapshot bundles."
keywords:
  - datasheet for datasets
  - benchmark dataset documentation
  - AOBench corpus provenance
---

# Datasheet for the AOBench corpus

Following the structure proposed in **Gebru et al., "Datasheets for Datasets"**
(*Communications of the ACM*, 2021). Answers describe AOBench **v0.4.1**. Where an
answer would change with a future release, that is stated.

Companion documents: the [benchmark card](benchmark-card.md) (intended use and misuse),
the [reproducibility notes](reproducing-results.md) (what is pinned), and the
[versioning policy](versioning.md) (what comparability means across releases).

---

## Motivation

**For what purpose was the dataset created?**
To make it possible to evaluate AI agents that operate High-Performance Computing
systems without giving those agents access to a real facility. Existing agent
benchmarks measure code repair, general assistance, or function calling; none measure
whether an agent can diagnose a failing job, interpret telemetry, respect an operator
role, and refuse a request outside its permissions. HPC centres considering
agent-assisted operations had no instrument with which to make that judgement.

**Who created the dataset and on behalf of whom?**
Mohsen Seyedkazemi Ardebili and Andrea Bartolini, Department of Electrical, Electronic
and Information Engineering (DEI), University of Bologna, Italy.

**Who funded the creation of the dataset?**
University of Bologna research activity. The Marconi100 operational data underlying the
grounded environments comes from CINECA's public ExaData release; AOBench neither
funded nor collected that measurement campaign.

---

## Composition

**What do the instances represent?**
Two linked artifact types:

1. **Task specifications** (88 JSON documents) — an operational question, the operator
   role asking it, the environment it is asked about, a gold trajectory of expected
   tool calls, gold evidence references, evaluation criteria, and RBAC metadata.
2. **Environment snapshot bundles** (29 directories) — frozen state for a cluster at a
   moment in time: Slurm job and node state, telemetry time series, site documentation,
   RBAC policy, and incident metadata.

**How many instances are there?**

| | Count |
|---|---:|
| Tasks | 88 |
| — synthetic core | 80 |
| — grounded in Marconi100 ExaData | 8 |
| Environments | 29 |
| — synthetic | 23 |
| — grounded in Marconi100 ExaData | 6 |
| Question categories (QCATs) | 10 |
| Operator roles | 5 |
| Dev-split tasks (open) | 67 |
| Test-split tasks (held out) | 21 |

Per-task and per-environment detail: [task catalog](../reference/task-catalog.md),
[environment catalog](../reference/environment-catalog.md).

**Does the dataset contain all possible instances or a sample?**
A sample, and a deliberately structured one: the synthetic core is a 10 QCAT × 5 role
design intended to give coverage across the operational space rather than to be
representative of any particular site's ticket distribution. **It is not a random
sample of real HPC operations, and no claim about the frequency of these scenarios in
the wild should be drawn from it.**

**What data does each instance consist of?**
Task specs are JSON conforming to the `TaskSpec` Pydantic model. Environment bundles
contain JSON (Slurm state, incidents), Parquet and CSV (telemetry), Markdown
(documentation), and YAML (RBAC policy, metadata).

**Is there a label or target?**
Yes. Each task carries a gold answer and/or a gold trajectory, gold evidence
references, and an evaluation mode (`exact_match`, `numeric`, `set`, or `rubric`).

**Is any information missing?**
Yes, and it matters:

- **No real RBAC policies.** Every RBAC policy in every bundle is synthetic, including
  in the M100-grounded environments. Real site authorisation models were not available.
- **No filesystem or MPI-level detail.** Storage and interconnect scenarios are
  represented at a coarse level.
- **No multi-turn dialogue.** Tasks are single queries; there is no simulated user.
- **Grounded bundles cover a subset of scenario types.** The six M100 bundles cover
  thermal, power, node-down, and job-failure scenarios; other categories remain
  synthetic.

**Are relationships between instances made explicit?**
Yes. Each task names its `environment_id`; each environment declares which roles and
categories it supports. Many tasks share an environment.

**Are there recommended data splits?**
Yes: 67 `dev` and 21 `test`. The test split is locked behind `AOBENCH_UNLOCK_TEST=1`
specifically to make training or tuning on it a deliberate act.

**Are there errors, noise, or redundancies?**
Certainly some, in a corpus this size that has not been independently re-annotated.
Gold answers are author-derived and reviewed but not multiply-annotated by
independent experts. **Reports of incorrect gold answers are treated as high-priority
bugs** — please [file them](https://github.com/MSKazemi/aobench/issues/new/choose).

**Is the dataset self-contained?**
Yes. Everything needed to run and score is in the repository and in the published
release archive. No network access and no external service is required. The M100
provenance references the public ExaData release, but the derived bundles stand alone.

**Does it contain confidential, personal, or offensive data?**
No. Synthetic bundles use invented users, accounts, and jobs. The M100-grounded
bundles derive from an already-public, anonymised research dataset; node and job
identifiers there refer to hardware and workloads, not to identifiable people. No
content is offensive or sensitive.

---

## Collection process

**How was the data acquired?**

- *Synthetic environments and tasks:* authored by the maintainers from HPC operational
  experience, site documentation conventions, and published incident patterns, then
  validated against a fidelity gate (F1–F7) that checks internal consistency —
  e.g. that telemetry actually shows the anomaly a task asks about, and that the gold
  evidence is genuinely present in the bundle.
- *Grounded environments:* derived from the public **Marconi100 ExaData** release
  (CINECA, 980-node Tier-0 system), by selecting real time windows exhibiting a
  scenario of interest, extracting the relevant Slurm records and telemetry channels,
  and packaging them in the AOBench bundle format. Each grounded bundle carries a
  `provenance.json` recording the source window and the transformation applied.

**Who was involved?**
The two maintainers. No crowdworkers were employed; no compensation question arises.

**Over what timeframe was the data collected?**
Corpus authoring: 2026. Underlying M100 telemetry: 2020–2022 operational windows, as
published by CINECA in ExaData.

**Was an ethical review process conducted?**
No formal IRB review was sought, and none is applicable: the corpus contains no human
subjects data. The underlying ExaData release was published by CINECA under its own
terms. See [ethics](ethics.md) for the responsible-use discussion that does apply.

---

## Preprocessing, cleaning, labelling

**Was any preprocessing done?**
Yes, for the grounded bundles: time-window selection, channel subsetting, resampling
to a common cadence, and reformatting to the bundle schema. Synthetic RBAC policies
and site documentation were added because ExaData contains neither.

**Was the raw data saved?**
The ExaData source is public and independently archived by CINECA, so AOBench does not
re-host it; `provenance.json` records exactly which window each bundle came from so the
derivation can be re-run.

**Is the preprocessing software available?**
Yes — the importer is in `scripts/`, under the same Apache-2.0 licence.

---

## Uses

**What has the dataset been used for?**
Evaluating hosted and open-weight models as HPC agents through the AOBench adapters,
and ablation studies over scoring dimensions.

**What other tasks could it be used for?**
Studying tool-selection behaviour, permission-boundary behaviour under pressure,
grounding and hallucination in operational contexts, and as a source of realistic
HPC operational scenarios for teaching.

**Is there anything about its composition that could cause unfair treatment or harm?**
The corpus encodes a particular view of what correct HPC operation looks like, drawn
largely from European Tier-0 practice. A site with different conventions could see its
correct-for-them behaviour scored as wrong. Roles are also a simplification: real
authorisation is finer-grained than five roles.

**Are there tasks for which it should not be used?**
Yes — see [limitations](limitations.md) and the
[benchmark card](benchmark-card.md#out-of-scope-uses). In particular: a high AOBench
score is **not** evidence that an agent is safe to run against production
infrastructure, and must not be cited as such.

---

## Distribution

**How is it distributed?**
In the [GitHub repository](https://github.com/MSKazemi/aobench) (and its GitLab
mirror), inside the published Python package, and as archived release deposits with
DOIs.

**When?** Continuously since the first public release; each tagged release is archived.

**Under what licence?** Apache-2.0, code and corpus alike.

**Have any third parties imposed restrictions?**
The derived M100 bundles depend on CINECA's public ExaData release; users publishing
results on grounded environments should cite ExaData as well as AOBench — see
[how to cite](citation.md).

**Are there export controls or regulatory restrictions?** None known.

---

## Maintenance

**Who maintains it?** The maintainers listed in
[MAINTAINERS.md](https://github.com/MSKazemi/aobench/blob/main/MAINTAINERS.md).

**How can they be contacted?** Through
[issues](https://github.com/MSKazemi/aobench/issues) or
[discussions](https://github.com/MSKazemi/aobench/discussions).

**Will the dataset be updated?**
Yes. Tasks and environments are added between minor versions. Every release is tagged
and archived so an old result stays re-derivable, and the
[versioning policy](versioning.md) states which changes break score comparability.

**Is there an erratum?**
Corrections are recorded in [CHANGELOG.md](changelog.md); a corpus correction that
invalidates published numbers is called out explicitly there.

**Will older versions continue to be supported?**
Old versions remain permanently available via their release tags and DOIs. They are
not actively maintained, but they will not disappear — which is the property a
published result actually needs.

**Can others extend or contribute?**
Yes, and contributions of tasks and environments are the most valuable kind. See
[adding a task](contributing.md) and
[adding an environment](../framework/environments.md). A sanitised snapshot from
a real facility is worth more than any amount of synthetic authoring.
