"""Tests for result attestation (Feature 25)."""

from __future__ import annotations

from aobench.reproducibility.attestation import (
    attest_run,
    build_statement,
    sha256_hex,
    sign_statement,
    verify_statement,
)

KEY = "test-signing-key"


def test_sha256_deterministic():
    a = sha256_hex({"b": 1, "a": 2})
    b = sha256_hex({"a": 2, "b": 1})  # key order independent (canonical json)
    assert a == b
    assert len(a) == 64


def test_build_statement_shape():
    st = build_statement("aobench-run:r1", "deadbeef", {"run_id": "r1"})
    assert st["_type"].endswith("Statement/v1")
    assert st["subject"][0]["digest"]["sha256"] == "deadbeef"
    assert st["predicate"]["run_id"] == "r1"


def test_sign_verify_roundtrip():
    st = build_statement("s", "abc", {"x": 1})
    sig = sign_statement(st, key=KEY)
    assert verify_statement(st, sig, key=KEY) is True


def test_verify_detects_tamper():
    st = build_statement("s", "abc", {"x": 1})
    sig = sign_statement(st, key=KEY)
    st["predicate"]["x"] = 999  # tamper
    assert verify_statement(st, sig, key=KEY) is False


def test_verify_wrong_key_fails():
    st = build_statement("s", "abc", {"x": 1})
    sig = sign_statement(st, key=KEY)
    assert verify_statement(st, sig, key="other-key") is False


def test_attest_run_bundles_and_signs():
    result = {"run_id": "r1", "aggregate_score": 0.8}
    trace = {"steps": [1, 2, 3]}
    att = attest_run(
        result, trace, run_id="r1",
        env_manifest_sha256="envhash", fingerprint={"seed": 7}, key=KEY,
    )
    assert att.signature is not None
    assert att.statement["predicate"]["env_manifest_sha256"] == "envhash"
    assert att.statement["predicate"]["result_sha256"] == sha256_hex(result)
    # the signature verifies against the produced statement
    assert verify_statement(att.statement, att.signature, key=KEY) is True


def test_attest_run_unsigned():
    att = attest_run({"a": 1}, {"b": 2}, run_id="r2", sign=False)
    assert att.signature is None
