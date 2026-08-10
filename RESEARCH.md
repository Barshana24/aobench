# Open research questions

AOBench exists because some questions about operational AI agents could not be asked
empirically. These are the ones we think are now answerable, and would like someone to
answer. **Several are good MSc or PhD projects; some are a good afternoon.**

If one of these interests you, open a
[discussion](https://github.com/MSKazemi/aobench/discussions) — we will help with the
setup, and we are happy for you to publish first-author. Co-supervision is possible for
students at any institution.

---

## Governance and authorisation

### R1 — Does explicit role framing change permission compliance?
Agents are told their role in the prompt. Does making the role and its boundaries more
explicit reduce RBAC violations, or does it merely teach the agent to describe the
boundary while still crossing it? **Method:** ablate the system-prompt role prefix
across the corpus; compare governance hard-fail rates. *Small project; the plumbing
already exists via `--system-prompt-prefix`.*

### R2 — Do capable agents overstep more?
There is a plausible and worrying hypothesis that agents which are better at the task
are *more* likely to violate their role, because they can see the shortcut. **Method:**
correlate outcome score against hard-fail rate across models. If the correlation is
positive, that is a genuinely important finding for anyone deploying these systems.

### R3 — Refusal calibration
An agent that refuses everything scores perfectly on governance if governance is naive.
AOBench uses engagement-aware grading to prevent that. How well does it work — and what
is the right trade-off curve between over-refusal and overreach for an operational
agent?

## Grounding and hallucination

### R4 — Does tool access reduce hallucination, or relocate it?
The `direct_qa` baseline hallucinates freely. Do tool-using agents actually ground their
answers, or do they call a tool and then answer from parametric knowledge anyway?
**Method:** compare the grounding dimension against tool-use dimension per task; look
for the high-tool-use / low-grounding quadrant.

### R5 — Evidence attribution quality
When an agent cites evidence, is the citation the evidence it actually used? A
trace-level study of claimed versus load-bearing evidence.

## Consistency and reliability

### R6 — What drives pass^k collapse?
Agents that pass single-shot often fail pass^5. Is the variance in tool selection, in
argument construction, or in the final synthesis? **Method:** decompose per-attempt
traces at k=10 by where they diverge. *This is the study we most want to see.*

### R7 — Does self-consistency help operations?
Sampling several traces and voting works for reasoning benchmarks. Does it work when
the failure mode is a wrong tool call rather than a wrong inference?

## Domain transfer

### R8 — Does HPC operational ability transfer from adjacent domains?
Do agents trained or tuned on SRE, DevOps, or general sysadmin data do better on
AOBench than general models of the same size? A question about whether "operations" is
one skill or many.

### R9 — Synthetic versus real environments
AOBench has 23 synthetic and 6 real-data environments. **Do agents score systematically
differently on the grounded ones?** If synthetic environments are easier, that is a
measurable indictment of synthetic benchmark data generally — and we would rather know.
*This is directly checkable today with `aobench list envs --grounded`.*

### R10 — Cross-site generalisation
Every environment reflects European Tier-0 conventions. Would an agent tuned on this
corpus generalise to a US or Japanese facility's practice? Needs a contributed
environment from elsewhere — see
[adding an environment](https://mskazemi.com/aobench/latest/guides/adding-an-environment/).

## Measurement methodology

### R11 — How much does the judge model matter?
Rubric-path tasks depend on an LLM judge. Run the same traces past several judges and
quantify the disagreement, including self-preference when the judge and the agent share
a model family.

### R12 — Is the weight profile defensible?
`default_hpc_v01` weights are a judgement call. Does the model ranking change under
different plausible profiles? If the ranking is weight-invariant, that strengthens
every AOBench result; if it is not, the profile needs justification we have not yet
given it. *Runnable today with `aobench rescore`.*

### R13 — Contamination measurement
Task specs are public. Can contamination be detected by comparing performance on tasks
added before versus after a model's training cutoff?

### R14 — How many tasks are enough?
With 88 tasks, what is the actual confidence interval on a model comparison, and how
many tasks would a given effect size need? A power analysis would tell us how much
corpus growth is worth.

## Systems and scale

### R15 — Cost-quality frontier for operational agents
CLEAR includes cost. Where is the knee? Is a small model with good tools better value
than a large model without them — the question every HPC centre with a budget actually
has.

### R16 — Live execution versus snapshots
AOBench's snapshots trade realism for reproducibility
([issue #19](https://github.com/MSKazemi/aobench/issues/19) tracks a containerised
runner). How large is the gap? A paired study on the same tasks would tell us how much
to trust snapshot-based evaluation generally — a result useful well beyond AOBench.

---

## Working with us

- **Data:** everything is Apache-2.0 and needs no permission.
- **Compute:** the deterministic path and `direct_qa` are free; hosted-model runs are
  the only real cost.
- **Reproducibility:** pin the version, report split + profile + dated model — see the
  [versioning policy](https://mskazemi.com/aobench/latest/about/versioning/).
- **Publishing:** please cite the version you ran ([CITATION.bib](CITATION.bib)), and
  tell us in Discussions so we can link your paper from the docs.

**Negative results are welcome here.** "We tried X and it did not help" is a real
contribution to a young field, and this project will link it rather than bury it.
