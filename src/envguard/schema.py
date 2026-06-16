"""Schema loading and the core validation routine."""

from __future__ import annotations

import tomllib
from pathlib import Path

from .validators import VALIDATORS, validate_value

# Result statuses.
OK = "OK"
MISSING = "MISSING"
INVALID = "INVALID"


class SchemaError(Exception):
    """Raised when the schema file is malformed."""


def load_schema(path):
    """Load and validate the structure of a schema TOML file.

    The file maps variable names to a table of options::

        [DATABASE_URL]
        required = true
        type = "url"

    Returns a dict ``{var_name: spec_dict}``.
    """
    path = Path(path)
    if not path.exists():
        raise SchemaError(f"schema file not found: {path}")

    with path.open("rb") as handle:
        try:
            data = tomllib.load(handle)
        except tomllib.TOMLDecodeError as exc:
            raise SchemaError(f"invalid TOML in {path}: {exc}") from exc

    schema = {}
    for name, spec in data.items():
        if not isinstance(spec, dict):
            raise SchemaError(
                f"variable {name!r} must be a table, got {type(spec).__name__}"
            )
        type_name = spec.get("type", "string")
        if type_name not in VALIDATORS:
            raise SchemaError(
                f"variable {name!r} has unknown type {type_name!r}"
            )
        if type_name == "enum" and not spec.get("values"):
            raise SchemaError(
                f"variable {name!r} of type enum requires a 'values' list"
            )
        if type_name == "regex" and not spec.get("pattern"):
            raise SchemaError(
                f"variable {name!r} of type regex requires a 'pattern'"
            )
        schema[name] = spec

    return schema


def parse_env_file(path):
    """Parse a simple ``.env`` file into a dict.

    Supports ``KEY=VALUE`` lines, ``#`` comments, blank lines, an optional
    leading ``export``, and surrounding single/double quotes on values.
    """
    path = Path(path)
    if not path.exists():
        raise SchemaError(f"env file not found: {path}")

    env = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        env[key] = value
    return env


def validate_environment(schema, environ):
    """Validate ``environ`` (a mapping) against ``schema``.

    Returns a list of result dicts with keys ``variable``, ``status`` and
    ``detail``, one per variable declared in the schema.
    """
    results = []
    for name, spec in schema.items():
        required = spec.get("required", False)
        default = spec.get("default")

        if name in environ:
            value = environ[name]
            ok, detail = validate_value(value, spec)
            status = OK if ok else INVALID
            results.append({"variable": name, "status": status, "detail": detail})
            continue

        if default is not None:
            value = str(default)
            ok, detail = validate_value(value, spec)
            if ok:
                results.append(
                    {
                        "variable": name,
                        "status": OK,
                        "detail": f"default applied ({value!r})",
                    }
                )
            else:
                results.append(
                    {
                        "variable": name,
                        "status": INVALID,
                        "detail": f"default {value!r} invalid: {detail}",
                    }
                )
            continue

        if required:
            results.append(
                {"variable": name, "status": MISSING, "detail": "required but not set"}
            )
        else:
            results.append(
                {"variable": name, "status": OK, "detail": "optional, not set"}
            )

    return results
