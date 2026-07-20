# Tutorial — Serve the benchmark over REST and MCP

This tutorial walks you from a fresh checkout to driving the AOBench engine
programmatically over both the REST API and an MCP client. By the end you will
run and score a task without touching the CLI's scoring path — because every
surface calls the same `BenchmarkService` façade, the results are identical.

**Prerequisites:** Python ≥ 3.12, `uv`, and this repository checked out.

Related reference: [Programmatic access guide](../guides/programmatic-access.md) ·
[`aobench serve` command reference](../reference/commands.md#serve).

---

## 1. Install the server extras

The REST and MCP servers are optional extras. Install them together (per-extra
`uv sync` is exclusive and would drop the others):

```bash
uv sync --extra rest --extra mcp
```

Confirm the commands are wired in:

```bash
uv run aobench serve --help
```

You should see `rest` and `mcp` subcommands.

---

## 2. Start the REST API

```bash
uv run aobench serve rest --host 127.0.0.1 --port 8000
```

Leave it running and open a second shell for the requests below.

### 2a. Discover tasks and environments

```bash
curl -s localhost:8000/v1/tasks   | jq 'length'      # number of task specs
curl -s localhost:8000/v1/envs    | jq '.[0]'        # first environment bundle
curl -s localhost:8000/v1/datasets | jq .            # dataset versions + split counts
```

### 2b. Run and score a task (synchronous)

```bash
curl -s -X POST localhost:8000/v1/runs \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"JOB_USR_001","env_id":"env_01","adapter":"direct_qa"}' \
  | jq '{run_id, clear, score: .result.aggregate_score}'
```

The response carries the full result — the same object `aobench run task` would
produce, including the CLEAR breakdown.

### 2c. Run asynchronously and poll a job

For long runs, submit with `wait=false` to get a job handle immediately:

```bash
JOB=$(curl -s -X POST 'localhost:8000/v1/runs?wait=false' \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"JOB_USR_001","env_id":"env_01","adapter":"direct_qa"}' \
  | jq -r .job_id)

curl -s localhost:8000/v1/jobs/$JOB | jq '{state, run_id}'
```

Poll until `state` is `completed`, then fetch the run via `/v1/runs/{run_id}`.

### 2d. Stream progress with Server-Sent Events

```bash
curl -N localhost:8000/v1/runs/<run_id>/events
```

Each event line reports a step of the run as it happens.

### 2e. Authentication (optional)

The API maps an `X-API-Key` header to a role, with per-role rate limiting.
Unauthenticated requests fall back to a read-only role. Send a key like:

```bash
curl -s localhost:8000/v1/tasks -H 'X-API-Key: <your-key>'
```

---

## 3. Drive the engine from an MCP client

The MCP server runs over stdio; an MCP client launches it as a subprocess:

```bash
uv run aobench serve mcp
```

Configure your MCP client to spawn that command. It then exposes:

- **Tools** — `run_task`, `score_trace`, `validate_benchmark`, `robustness`.
- **Resources** — `aobench://tasks`, `aobench://tasks/{id}`, `aobench://envs`,
  `aobench://runs/{id}/report`, `aobench://runs/{id}/trace`.

Calling the `run_task` tool with `{"task_id": "JOB_USR_001", "env_id": "env_01",
"adapter": "direct_qa"}` returns the same result object as the REST `POST /v1/runs`
call in step 2b — identical scoring, different transport.

---

## 4. Verify surfaces agree

Run the same task via the CLI and via REST, then compare the `aggregate_score`:

```bash
uv run aobench run task --task JOB_USR_001 --env env_01 --adapter direct_qa
# vs. the /v1/runs response from step 2b
```

Both paths route through `BenchmarkService`, so the scores match. That
invariant — one façade, many transports — is what lets you benchmark an agent
over whichever surface it actually speaks.

---

## Next steps

- [Programmatic access guide](../guides/programmatic-access.md) — full endpoint,
  tool, and resource tables.
- [ROADMAP](https://github.com/MSKazemi/aobench/blob/main/ROADMAP.md) — surface status
  (A2A and CLI *access* transports are the infra-gated remainder).
- [System architecture](../framework/system-architecture.md) — where the façade sits
  in the layered design.
