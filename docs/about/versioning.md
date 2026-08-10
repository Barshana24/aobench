---
title: "AOBench versioning and score comparability policy"
description: "How AOBench versions the benchmark corpus and scoring profiles, which changes break score comparability across releases, and what to report so your numbers stay meaningful."
keywords:
  - benchmark versioning
  - score comparability
  - reproducible evaluation
---

# Versioning and score comparability

A benchmark whose corpus changes silently produces numbers nobody can compare. This
page states exactly what AOBench promises across versions, and what it does not.

## The short version

**AOBench scores are comparable within a version. Across versions, only if this page
says so.** Always report the version, the split, the profile, and the adapter.

## What the version number means

AOBench uses semantic versioning with benchmark-specific meanings:

| Change | Bump | Score comparability |
|---|---|---|
| Bug fix in a scorer that corrects a wrong result | **patch** | **Broken** — old numbers were wrong |
| Bug fix with no scoring effect (CLI, docs, packaging) | patch | Preserved |
| New task or environment added | **minor** | Broken for whole-split scores; preserved per-task |
| Gold answer corrected | **minor** | Broken for that task; noted in the changelog |
| Weight profile retuned | **minor** | Broken for aggregate scores; per-dimension preserved |
| New dimension or scorer added | **minor** | Broken for aggregate scores |
| Task schema change requiring corpus migration | **major** | Broken |
| Split reassignment | **major** | Broken |

"Broken" means: do not compare a number produced under one version with a number
produced under another, and do not silently update a published table.

## What is guaranteed within a version

Given the same version, the same split, the same profile, the same adapter, and the
same model:

- **Deterministic-path tasks produce identical scores.** Byte-identical snapshots and
  no model in the scoring loop.
- **Environment bundles are byte-stable.** They are versioned files, not generated.
- **Task IDs are stable.** A task ID never gets reused for different content.

Not guaranteed, even within a version:

- **Rubric-path scores**, which depend on a judge model that the AOBench version does
  not pin.
- **The agent's own output**, if the model behind the adapter is non-deterministic or
  the provider updates it under a moving alias like `gpt-4o`.

That second one bites more often than people expect: **pin the dated model snapshot,
not the alias**, or your own re-run will not reproduce.

## Reporting a result

Report all four. A number without them is not interpretable:

```text
AOBench v0.4.1 · split=dev · profile=default_hpc_v01 · adapter=openai:gpt-4o-2024-11-20
```

If any task used the rubric path, add the judge model. If you used `--n` for
robustness, add k. If you used a custom profile, say so loudly — a custom profile makes
your number incomparable with everyone else's by construction.

`aobench report json` emits all of this in the run metadata, so the honest path is also
the easy one: quote the metadata block.

## Retractions and errata

If a corpus or scorer bug is found that invalidates previously published numbers:

1. The fix lands with a version bump.
2. [CHANGELOG.md](changelog.md) records it under an explicit **score-affecting** heading,
   naming which tasks or dimensions moved.
3. If the effect is large, the release notes say so in the first paragraph.

We would rather publish an embarrassing correction than let a wrong number propagate.
If you have published a number that a later correction invalidates, we will help you
work out the delta — [open a discussion](https://github.com/MSKazemi/aobench/discussions).

## Long-term availability

Every tagged release is archived with a DOI, so a result from any version stays
re-derivable. Old versions are not maintained, but they do not disappear — which is the
property a citation actually needs.

Cite the **version DOI** for a specific result, and the **concept DOI** when you mean
the project in general. Both are in [how to cite](citation.md).

## Deprecation policy

Public surfaces — CLI commands and flags, the REST and MCP APIs, the task schema —
follow this sequence:

1. **Announced** in the changelog with the replacement named.
2. **Warned** at runtime for at least one minor version.
3. **Removed** no earlier than the next minor version after the warning.

Anything prefixed with `_`, and anything under `scripts/`, is internal and may change
without notice.
