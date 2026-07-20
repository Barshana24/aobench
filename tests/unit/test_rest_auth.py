"""Unit tests for REST auth + rate limiting (spec-0003 R3/R4)."""

from __future__ import annotations

import pytest

from aobench.server.rest import auth


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("AOBENCH_API_KEYS", raising=False)
    monkeypatch.delenv("AOBENCH_RATE_LIMIT_PER_MIN", raising=False)
    auth.reset_rate_limits()
    yield
    auth.reset_rate_limits()


# --------------------------------------------------------------------------- #
# identity resolution
# --------------------------------------------------------------------------- #
def test_open_dev_mode_resolves_admin():
    assert auth.resolve_identity(None).role == "admin"  # no keys configured
    assert auth.resolve_identity("anything").tenant == "dev"


def test_configured_key_maps_to_role(monkeypatch):
    monkeypatch.setenv("AOBENCH_API_KEYS", "k1secretkey:hpc_user, k2:admin")
    assert auth.resolve_identity("k1secretkey").role == "hpc_user"
    assert auth.resolve_identity("k2").role == "admin"


def test_unknown_key_fails(monkeypatch):
    monkeypatch.setenv("AOBENCH_API_KEYS", "k1:admin")
    assert auth.resolve_identity("nope") is None
    assert auth.resolve_identity(None) is None


def test_malformed_pairs_skipped(monkeypatch):
    # blank entries and a pair with no colon are ignored; empty role → hpc_user default
    monkeypatch.setenv("AOBENCH_API_KEYS", " , nocolon , k3: ")
    assert auth.resolve_identity("nocolon") is None
    assert auth.resolve_identity("k3").role == "hpc_user"


# --------------------------------------------------------------------------- #
# rate limiting
# --------------------------------------------------------------------------- #
def test_rate_limit_allows_within_budget(monkeypatch):
    monkeypatch.setenv("AOBENCH_RATE_LIMIT_PER_MIN", "3")
    assert all(auth.check_rate_limit("k", now=100.0) for _ in range(3))
    assert auth.check_rate_limit("k", now=100.0) is False  # 4th exceeds


def test_rate_limit_resets_next_window(monkeypatch):
    monkeypatch.setenv("AOBENCH_RATE_LIMIT_PER_MIN", "1")
    assert auth.check_rate_limit("k", now=100.0) is True
    assert auth.check_rate_limit("k", now=100.0) is False
    assert auth.check_rate_limit("k", now=200.0) is True  # new window


def test_rate_limit_disabled_when_zero(monkeypatch):
    monkeypatch.setenv("AOBENCH_RATE_LIMIT_PER_MIN", "0")
    assert all(auth.check_rate_limit("k", now=100.0) for _ in range(50))


def test_rate_limit_bad_value_falls_back(monkeypatch):
    monkeypatch.setenv("AOBENCH_RATE_LIMIT_PER_MIN", "not-an-int")
    assert auth.check_rate_limit("k", now=100.0) is True  # default 10000
