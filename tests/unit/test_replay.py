"""Tests for the deterministic replay engine (Feature 24)."""

from __future__ import annotations

import pytest

from aobench.reproducibility.replay import (
    Cassette,
    ReplayMiss,
    ReplaySession,
    make_key,
)


# --------------------------------------------------------------------------- #
# make_key
# --------------------------------------------------------------------------- #
def test_make_key_deterministic():
    k1 = make_key(task_id="T", env_id="e", model="gpt-4o", prompt="hi", seed=1)
    k2 = make_key(task_id="T", env_id="e", model="gpt-4o", prompt="hi", seed=1)
    assert k1 == k2
    assert len(k1) == 64  # sha256 hex


@pytest.mark.parametrize("field,val", [
    ("task_id", "T2"), ("env_id", "e2"), ("model", "gpt-4o-mini"),
    ("prompt", "bye"), ("seed", 2),
])
def test_make_key_sensitive_to_each_field(field, val):
    base = dict(task_id="T", env_id="e", model="gpt-4o", prompt="hi", seed=1)
    changed = dict(base)
    changed[field] = val
    assert make_key(**base) != make_key(**changed)


def test_make_key_structured_prompt():
    k = make_key(task_id="T", env_id="e", model="m",
                 prompt=[{"role": "user", "content": "x"}])
    assert isinstance(k, str) and len(k) == 64


# --------------------------------------------------------------------------- #
# ReplaySession modes
# --------------------------------------------------------------------------- #
def test_live_records():
    s = ReplaySession(mode="live")
    calls = []

    def producer():
        calls.append(1)
        return {"answer": 42}

    key = make_key(task_id="T", env_id="e", model="m", prompt="p")
    out = s.respond(key, producer)
    assert out == {"answer": 42}
    assert key in s.cassette
    assert s.recorded == 1
    assert len(calls) == 1


def test_replay_serves_recorded_without_calling_producer():
    cas = Cassette({make_key(task_id="T", env_id="e", model="m", prompt="p"): {"a": 1}})
    s = ReplaySession(cassette=cas, mode="replay")

    key = make_key(task_id="T", env_id="e", model="m", prompt="p")
    out = s.respond(key, lambda: pytest.fail("producer must not be called in replay"))
    assert out == {"a": 1}
    assert s.hits == 1


def test_replay_miss_raises():
    s = ReplaySession(mode="replay")
    with pytest.raises(ReplayMiss):
        s.respond("missing", lambda: 1)
    assert s.misses == 1


def test_auto_serves_then_tops_up():
    s = ReplaySession(mode="auto")
    key = make_key(task_id="T", env_id="e", model="m", prompt="p")
    # first call: miss → produce+record
    assert s.respond(key, lambda: "v1") == "v1"
    # second call: hit → serve recorded, ignore producer
    assert s.respond(key, lambda: "v2") == "v1"
    assert s.hits == 1 and s.recorded == 1


def test_invalid_mode():
    with pytest.raises(ValueError):
        ReplaySession(mode="bogus")


# --------------------------------------------------------------------------- #
# Cassette persistence
# --------------------------------------------------------------------------- #
def test_cassette_save_load_roundtrip(tmp_path):
    path = tmp_path / "cassette.json"
    s = ReplaySession(mode="live")
    key = make_key(task_id="T", env_id="e", model="m", prompt="p")
    s.respond(key, lambda: {"x": [1, 2, 3]})
    s.cassette.save(path)

    loaded = Cassette.load(path)
    assert key in loaded
    assert loaded.get(key) == {"x": [1, 2, 3]}


def test_replay_from_loaded_cassette_is_bit_reproducible(tmp_path):
    path = tmp_path / "c.json"
    # record
    rec = ReplaySession(mode="live")
    key = make_key(task_id="T", env_id="e", model="m", prompt="p", seed=7)
    rec.respond(key, lambda: {"tokens": 123, "text": "answer"})
    rec.cassette.save(path)

    # replay in a fresh session
    rep = ReplaySession(cassette=Cassette.load(path), mode="replay")
    out = rep.respond(key, lambda: pytest.fail("should not call producer"))
    assert out == {"tokens": 123, "text": "answer"}
