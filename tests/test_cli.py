"""Tests for the CLI entry point."""

import json

from envguard import cli


SCHEMA = """
[APP_NAME]
required = true
type = "string"

[PORT]
required = true
type = "int"

[DEBUG]
type = "bool"
default = false
"""


def _write_schema(tmp_path):
    path = tmp_path / "envguard.toml"
    path.write_text(SCHEMA, encoding="utf-8")
    return path


def test_cli_all_ok(tmp_path, monkeypatch, capsys):
    schema = _write_schema(tmp_path)
    monkeypatch.setenv("APP_NAME", "svc")
    monkeypatch.setenv("PORT", "8080")
    code = cli.main(["--schema", str(schema)])
    out = capsys.readouterr().out
    assert code == 0
    assert "VARIABLE" in out
    assert "OK" in out


def test_cli_missing_fails(tmp_path, monkeypatch, capsys):
    schema = _write_schema(tmp_path)
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    code = cli.main(["--schema", str(schema)])
    out = capsys.readouterr().out
    assert code == 1
    assert "MISSING" in out


def test_cli_env_file(tmp_path, monkeypatch, capsys):
    schema = _write_schema(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text("APP_NAME=svc\nPORT=9090\n", encoding="utf-8")
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    code = cli.main(["--schema", str(schema), "--env-file", str(env_file)])
    out = capsys.readouterr().out
    assert code == 0
    assert "OK" in out


def test_cli_invalid_value(tmp_path, monkeypatch, capsys):
    schema = _write_schema(tmp_path)
    monkeypatch.setenv("APP_NAME", "svc")
    monkeypatch.setenv("PORT", "not-int")
    code = cli.main(["--schema", str(schema)])
    out = capsys.readouterr().out
    assert code == 1
    assert "INVALID" in out


def test_cli_missing_schema(tmp_path, capsys):
    code = cli.main(["--schema", str(tmp_path / "nope.toml")])
    err = capsys.readouterr().err
    assert code == 2
    assert "error" in err


def test_cli_json_structure_and_ok(tmp_path, monkeypatch, capsys):
    schema = _write_schema(tmp_path)
    monkeypatch.setenv("APP_NAME", "svc")
    monkeypatch.setenv("PORT", "8080")
    code = cli.main(["--schema", str(schema), "--format", "json"])
    out = capsys.readouterr().out
    assert code == 0

    data = json.loads(out)
    assert isinstance(data, list)
    assert len(data) == 3
    for entry in data:
        assert set(entry) == {"variable", "status", "detail"}
        assert entry["status"] in ("ok", "missing", "invalid")

    by_name = {e["variable"]: e for e in data}
    assert by_name["APP_NAME"]["status"] == "ok"
    assert by_name["PORT"]["status"] == "ok"


def test_cli_json_missing_status_and_exit_code(tmp_path, monkeypatch, capsys):
    schema = _write_schema(tmp_path)
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    code = cli.main(["--schema", str(schema), "--format", "json"])
    out = capsys.readouterr().out
    assert code == 1

    data = json.loads(out)
    by_name = {e["variable"]: e for e in data}
    assert by_name["APP_NAME"]["status"] == "missing"
    assert by_name["PORT"]["status"] == "missing"


def test_cli_json_invalid_status(tmp_path, monkeypatch, capsys):
    schema = _write_schema(tmp_path)
    monkeypatch.setenv("APP_NAME", "svc")
    monkeypatch.setenv("PORT", "not-int")
    code = cli.main(["--schema", str(schema), "--format", "json"])
    out = capsys.readouterr().out
    assert code == 1

    data = json.loads(out)
    by_name = {e["variable"]: e for e in data}
    assert by_name["PORT"]["status"] == "invalid"


def test_cli_json_has_no_table_summary(tmp_path, monkeypatch, capsys):
    schema = _write_schema(tmp_path)
    monkeypatch.setenv("APP_NAME", "svc")
    monkeypatch.setenv("PORT", "8080")
    cli.main(["--schema", str(schema), "--format", "json"])
    out = capsys.readouterr().out
    assert "VARIABLE" not in out
    assert "total" not in out
