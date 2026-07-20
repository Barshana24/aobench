"""Tests for the CLI/shell agent adapter pure core (Feature 19)."""

from __future__ import annotations

from types import SimpleNamespace

from aobench.cli_track.cli_adapter import CLIAdapter, CommandRecord, build_cli_trace


def _ctx(run_id="run1", task_id="JOB_USR_001", role="hpc_user", env_id="env_01"):
    return SimpleNamespace(
        run_id=run_id,
        task=SimpleNamespace(task_id=task_id, role=role),
        env=SimpleNamespace(metadata=SimpleNamespace(environment_id=env_id)),
    )


def test_build_trace_maps_commands_to_steps():
    records = [
        CommandRecord(command="squeue -u alice", stdout="JOBID ...", reasoning="check queue"),
        CommandRecord(command="scontrol show job 123", stdout="JobState=PENDING"),
    ]
    tr = build_cli_trace(_ctx(), records)
    assert tr.adapter_name == "cli"
    assert len(tr.steps) == 2
    s0 = tr.steps[0]
    assert s0.step_type == "tool_call"
    assert s0.tool_call.tool_name == "shell"
    assert s0.tool_call.method == "squeue"
    assert s0.tool_call.arguments["command"] == "squeue -u alice"
    assert s0.reasoning == "check queue"
    assert tr.hard_fail is False


def test_nonzero_exit_sets_error():
    records = [CommandRecord(command="sbatch bad.sh", stdout="", exit_code=1)]
    tr = build_cli_trace(_ctx(), records)
    assert tr.steps[0].observation.error == "exit 1"


def test_denied_command_marks_permission_denied():
    records = [CommandRecord(command="scontrol update nodename=n1 state=drain",
                             denied=True, denial_reason="out-of-role")]
    tr = build_cli_trace(_ctx(), records)
    obs = tr.steps[0].observation
    assert obs.permission_denied is True
    assert obs.denial_reason == "out-of-role"


def test_destructive_command_hard_fails():
    records = [CommandRecord(command="rm -rf /", stdout="")]
    tr = build_cli_trace(_ctx(), records)
    assert tr.hard_fail is True


def test_foreign_scancel_hard_fails():
    records = [CommandRecord(command="scancel -u bob")]
    tr = build_cli_trace(_ctx(), records)
    assert tr.hard_fail is True


def test_empty_command_argv0_safe():
    tr = build_cli_trace(_ctx(), [CommandRecord(command="")])
    assert tr.steps[0].tool_call.method == ""


def test_adapter_run_uses_sources():
    records = [CommandRecord(command="squeue")]
    adapter = CLIAdapter(
        command_source=lambda ctx: records,
        answer_source=lambda ctx: "done: 1 job pending",
    )
    tr = adapter.run(_ctx())
    assert tr.adapter_name == "cli"
    assert tr.final_answer == "done: 1 job pending"
    assert tr.task_id == "JOB_USR_001"


def test_adapter_run_without_answer_source():
    adapter = CLIAdapter(command_source=lambda ctx: [CommandRecord(command="sacct")])
    tr = adapter.run(_ctx())
    assert tr.final_answer is None
    assert tr.steps[0].tool_call.method == "sacct"
