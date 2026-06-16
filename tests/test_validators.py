"""Tests for the individual value validators."""

import pytest

from envguard.validators import validate_value


@pytest.mark.parametrize("value", ["0", "42", "-7"])
def test_int_valid(value):
    ok, _ = validate_value(value, {"type": "int"})
    assert ok


@pytest.mark.parametrize("value", ["", "1.5", "abc", "3x"])
def test_int_invalid(value):
    ok, _ = validate_value(value, {"type": "int"})
    assert not ok


@pytest.mark.parametrize("value", ["1.5", "42", "-0.3", "1e3"])
def test_float_valid(value):
    ok, _ = validate_value(value, {"type": "float"})
    assert ok


@pytest.mark.parametrize("value", ["", "abc", "1,5"])
def test_float_invalid(value):
    ok, _ = validate_value(value, {"type": "float"})
    assert not ok


@pytest.mark.parametrize("value", ["true", "False", "1", "0", "yes", "no", "on", "off"])
def test_bool_valid(value):
    ok, _ = validate_value(value, {"type": "bool"})
    assert ok


@pytest.mark.parametrize("value", ["maybe", "2", "tru"])
def test_bool_invalid(value):
    ok, _ = validate_value(value, {"type": "bool"})
    assert not ok


@pytest.mark.parametrize(
    "value", ["https://example.com", "http://a.b/c?d=1", "ftp://host/file"]
)
def test_url_valid(value):
    ok, _ = validate_value(value, {"type": "url"})
    assert ok


@pytest.mark.parametrize("value", ["example.com", "not a url", "://nohost", ""])
def test_url_invalid(value):
    ok, _ = validate_value(value, {"type": "url"})
    assert not ok


@pytest.mark.parametrize("value", ["a@b.com", "user.name@sub.example.org"])
def test_email_valid(value):
    ok, _ = validate_value(value, {"type": "email"})
    assert ok


@pytest.mark.parametrize("value", ["plain", "a@b", "a@@b.com", "a b@c.com", ""])
def test_email_invalid(value):
    ok, _ = validate_value(value, {"type": "email"})
    assert not ok


def test_enum_membership():
    spec = {"type": "enum", "values": ["info", "debug"]}
    assert validate_value("info", spec)[0]
    assert not validate_value("trace", spec)[0]


def test_regex_match():
    spec = {"type": "regex", "pattern": r"v\d+\.\d+\.\d+"}
    assert validate_value("v1.2.3", spec)[0]
    assert not validate_value("1.2.3", spec)[0]
    assert not validate_value("v1.2.3-rc", spec)[0]


def test_string_always_valid():
    assert validate_value("anything", {"type": "string"})[0]


def test_unknown_type():
    ok, detail = validate_value("x", {"type": "nope"})
    assert not ok
    assert "unknown type" in detail
