"""Tests for ``scripts/generate_tool_docs.py`` role detection.

``_detect_role`` reads the primary role from an environment's ``metadata.yaml``
and is expected to answer ``None`` — never raise — whenever the file is missing,
unreadable, or does not carry a single unambiguous role. A snapshot bundle with
an empty or hand-truncated ``metadata.yaml`` is the realistic failure case: YAML
parses it to ``None``, which is not a mapping.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"


def _import_script(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


@pytest.fixture(scope="module")
def generate_tool_docs():
    return _import_script("generate_tool_docs")


def _env_with_metadata(tmp_path: Path, body: str) -> Path:
    env_dir = tmp_path / "env_test"
    env_dir.mkdir()
    (env_dir / "metadata.yaml").write_text(body, encoding="utf-8")
    return env_dir


def test_single_role_is_detected(generate_tool_docs, tmp_path: Path) -> None:
    env_dir = _env_with_metadata(tmp_path, "supported_roles:\n  - sysadmin\n")
    assert generate_tool_docs._detect_role(env_dir) == "sysadmin"


def test_several_roles_are_ambiguous(generate_tool_docs, tmp_path: Path) -> None:
    env_dir = _env_with_metadata(tmp_path, "supported_roles:\n  - sysadmin\n  - researcher\n")
    assert generate_tool_docs._detect_role(env_dir) is None


def test_missing_metadata_yields_none(generate_tool_docs, tmp_path: Path) -> None:
    env_dir = tmp_path / "env_bare"
    env_dir.mkdir()
    assert generate_tool_docs._detect_role(env_dir) is None


@pytest.mark.parametrize("body", ["", "\n", "# only a comment\n", "just-a-string\n"])
def test_non_mapping_metadata_yields_none_and_does_not_raise(
    generate_tool_docs, tmp_path: Path, body: str
) -> None:
    """An empty or scalar metadata.yaml parses to None/str, not a mapping.

    Reading ``supported_roles`` off that value raises ``AttributeError``, which is
    not an exception ``_detect_role`` catches — so the generator aborted mid-run
    instead of treating the role as undeclared.
    """
    env_dir = _env_with_metadata(tmp_path, body)
    assert generate_tool_docs._detect_role(env_dir) is None


def test_malformed_yaml_yields_none(generate_tool_docs, tmp_path: Path) -> None:
    env_dir = _env_with_metadata(tmp_path, "supported_roles: [unclosed\n")
    assert generate_tool_docs._detect_role(env_dir) is None
