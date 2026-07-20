"""Pydantic models for HPC snapshot bundle data files (slurm_state.json, incident_metadata.json)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class SlurmNode(BaseModel):
    name: str
    state: str
    cpus: int
    memory_mb: int
    partitions: list[str]


class SlurmPartition(BaseModel):
    name: str
    max_time: str
    max_mem_per_node_mb: Optional[int] = None
    default_mem_per_cpu_mb: Optional[int] = None


class SlurmJob(BaseModel):
    job_id: str
    user: str
    state: str
    partition: str
    job_name: Optional[str] = None
    account: Optional[str] = None
    exit_code: Optional[str] = None
    node: Optional[str] = None
    submit_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    elapsed: Optional[str] = None
    num_cpus: Optional[int] = None
    num_nodes: Optional[int] = None
    requested_mem_mb: Optional[int] = None
    used_mem_mb: Optional[int] = None
    oom_kill: bool = False
    failure_reason: Optional[str] = None

    # M100 ExaData (job_info_marconi100) compatibility fields — all optional so
    # existing bundles validate unchanged. Populated by M100-grounded environments
    # (scripts/build_m100_bundles.py) which mirror canonical fields above for the
    # tools/fidelity gate while preserving the real M100 vocabulary here.
    qos: Optional[str] = None
    job_state: Optional[str] = None
    derived_ec: Optional[str] = None
    run_time: Optional[int] = None              # seconds
    time_limit: Optional[str] = None
    priority: Optional[int] = None
    state_reason: Optional[str] = None
    nodes: Optional[list[str]] = None           # M100 allocated-node list
    min_memory_cpu: Optional[int] = None        # MB
    min_memory_node: Optional[int] = None        # MB
    eligible_time: Optional[datetime] = None


class SlurmState(BaseModel):
    cluster: str
    snapshot_time: datetime
    nodes: list[SlurmNode]
    partitions: list[SlurmPartition]
    jobs: list[SlurmJob]


class IncidentMetadata(BaseModel):
    incident_id: str
    severity: str
    title: str
    opened_at: datetime
    status: str
    affected_resource: Optional[str] = None
    affected_job: Optional[str] = None
    summary: str
    timeline: list[dict[str, Any]]
    resolution: Optional[str] = None
    notes: Optional[str] = None
