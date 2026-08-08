# Cite AOBench

If AOBench contributed to work you are publishing, please cite the software. Citing
research software is how the people who maintain it get credit that counts, and it lets
readers find the exact version your numbers came from.

## Cite the software

GitHub renders a **"Cite this repository"** button from [`CITATION.cff`][cff], which is the
authoritative metadata. In BibTeX:

```bibtex
@software{aobench,
  title     = {{AOBench}: A Trace-Driven, Role-Aware Benchmark for Agent
               Operations in Realistic Environments},
  author    = {Seyedkazemi Ardebili, Mohsen and Bartolini, Andrea},
  year      = {2026},
  version   = {0.4.0},
  license   = {Apache-2.0},
  url       = {https://github.com/MSKazemi/aobench},
  publisher = {GitHub}
}
```

**Cite the version you actually ran**, not `main`. Every release is tagged, and the
`version` field above should match the tag you used. Results from different versions are
not necessarily comparable — scoring profiles and the task corpus evolve between minor
versions.

## Machine-readable metadata

| File | Standard | Consumed by |
|---|---|---|
| [`CITATION.cff`][cff] | [Citation File Format](https://citation-file-format.github.io/) 1.2.0 | GitHub, Zenodo, citation managers |
| [`codemeta.json`][codemeta] | [CodeMeta](https://codemeta.github.io/) 3.0 | Research-software registries, OpenAIRE |
| [`.zenodo.json`][zenodo] | Zenodo deposition metadata | Zenodo, when a release is archived |

All three carry the same authors, ORCIDs, affiliation, licence and keywords. If you change
one, change all three — divergent metadata is worse than none, because downstream registries
will disagree about who wrote the software.

## Archival DOI

A DOI is minted per release once the repository is archived. When that is in place, cite
the **version DOI** for exact reproducibility, or the **concept DOI** if you mean "AOBench
in general". The concept DOI always resolves to the newest version.

## Also cite the data, where it applies

Six of the 29 environment snapshots and eight of the 88 tasks are grounded in the public
**Marconi100 ExaData** dataset. If your work depends on those, cite the dataset paper too —
the environments are derived from it, not independent of it:

```bibtex
@article{m100exadata,
  title   = {{M100 ExaData}: a data collection campaign on the {CINECA}'s
             {Marconi100} {Tier-0} supercomputer},
  author  = {Borghesi, Andrea and Di Santi, Carmine and Molan, Martin and
             Seyedkazemi Ardebili, Mohsen and Mauri, Alessio and
             Guarrasi, Massimiliano and Galetti, Daniela and Cestari, Mirko and
             Barchi, Francesco and Benini, Luca and Beneventi, Francesco and
             Bartolini, Andrea},
  journal = {Scientific Data},
  volume  = {10},
  number  = {1},
  pages   = {288},
  year    = {2023},
  doi     = {10.1038/s41597-023-02174-3}
}
```

## What to report alongside a number

If you publish an AOBench score, these four fields let a reader reproduce it. Without them
a score is not checkable, and an uncheckable benchmark number is not evidence:

| Report | Why |
|---|---|
| **Version tag** (e.g. `v0.4.0`) | Task corpus and scoring profiles change between versions |
| **Scoring profile** (e.g. `default_hpc_v01`) | Dimension weights differ between profiles |
| **Split** (`dev` or `test`) | The test split is held out; dev and test numbers are not interchangeable |
| **Adapter and model identifier** | `openai:gpt-4o` is not the same system as `direct_qa` |

See [Reproducing results](reproducing-results.md) for the full contract.

[cff]: https://github.com/MSKazemi/aobench/blob/main/CITATION.cff
[codemeta]: https://github.com/MSKazemi/aobench/blob/main/codemeta.json
[zenodo]: https://github.com/MSKazemi/aobench/blob/main/.zenodo.json
