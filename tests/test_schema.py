"""Tests for schema loading and environment validation."""

import pytest

from envguard.schema import (
    INVALID,
    MISSING,
    OK,
    SchemaError,
    load_schema,
    parse_env_file,
    validate_environment,
)


def _status(results, name):
    return next(r["status"] for r in results if r["variable"] == name)


def test_required_present_ok():
    schema = {"NAME": {"required": True, "type": "string"}}
    results = validate_environment(schema, {"NAME": "value"})
    assert _status(results, "NAME") == OK


def test_required_missing_fails():
    schema = {"NAME": {"required": True, "type": "string"}}
    results = validate_environment(schema, {})
    assert _status(results, "NAME") == MISSING


def test_optional_missing_is_ok():
    schema = {"NAME": {"required": False, "type": "string"}}
    results = validate_environment(schema, {})
    assert _status(results, "NAME") == OK


def test_invalid_value_fails():
    schema = {"PORT": {"required": True, "type": "int"}}
    results = validate_environment(schema, {"PORT": "abc"})
    assert _status(results, "PORT") == INVALID


def test_default_applied():
    schema = {"LEVEL": {"type": "enum", "values": ["info", "debug"], "default": "info"}}
    results = validate_environment(schema, {})
    result = next(r for r in results if r["variable"] == "LEVEL")
    assert result["status"] == OK
    assert "default applied" in result["detail"]


def test_default_overridden_by_env():
    schema = {"DEBUG": {"type": "bool", "default": False}}
    results = validate_environment(schema, {"DEBUG": "true"})
    assert _status(results, "DEBUG") == OK


def test_invalid_default_reported():
    schema = {"PORT": {"type": "int", "default": "not-a-number"}}
    results = validate_environment(schema, {})
    result = next(r for r in results if r["variable"] == "PORT")
    assert result["status"] == INVALID


def test_load_schema(tmp_path):
    path = tmp_path / "envguard.toml"
    path.write_text(
        '[DATABASE_URL]\nrequired = true\ntype = "url"\n', encoding="utf-8"
    )
    schema = load_schema(path)
    assert schema["DATABASE_URL"]["type"] == "url"


def test_load_schema_missing_file(tmp_path):
    with pytest.raises(SchemaError):
        load_schema(tmp_path / "nope.toml")


def test_load_schema_unknown_type(tmp_path):
    path = tmp_path / "envguard.toml"
    path.write_text('[X]\ntype = "weird"\n', encoding="utf-8")
    with pytest.raises(SchemaError):
        load_schema(path)


def test_load_schema_enum_requires_values(tmp_path):
    path = tmp_path / "envguard.toml"
    path.write_text('[X]\ntype = "enum"\n', encoding="utf-8")
    with pytest.raises(SchemaError):
        load_schema(path)


def test_parse_env_file(tmp_path):
    path = tmp_path / ".env"
    path.write_text(
        "# comment\n"
        "export FOO=bar\n"
        'QUOTED="hello world"\n'
        "SINGLE='x'\n"
        "\n"
        "EMPTY_OK=\n",
        encoding="utf-8",
    )
    env = parse_env_file(path)
    assert env["FOO"] == "bar"
    assert env["QUOTED"] == "hello world"
    assert env["SINGLE"] == "x"
    assert env["EMPTY_OK"] == ""


def test_parse_env_file_missing(tmp_path):
    with pytest.raises(SchemaError):
        parse_env_file(tmp_path / "nope.env")
