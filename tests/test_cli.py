"""Tests for the CLI entry point."""

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
