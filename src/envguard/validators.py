"""Value validators for the supported schema types.

Each validator takes the raw string value read from the environment and
returns ``(ok, detail)`` where ``ok`` is a bool and ``detail`` is a short
human-readable message describing the result or the reason for failure.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

# A pragmatic email pattern: something@something.tld with no spaces.
_EMAIL_RE = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

# Accepted truthy/falsy spellings for the bool type.
_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def validate_string(value, spec):
    """A string is always valid as long as it is present."""
    return True, "string"


def validate_int(value, spec):
    try:
        int(value)
    except (TypeError, ValueError):
        return False, f"expected int, got {value!r}"
    return True, "int"


def validate_float(value, spec):
    try:
        float(value)
    except (TypeError, ValueError):
        return False, f"expected float, got {value!r}"
    return True, "float"


def validate_bool(value, spec):
    if value.lower() in _TRUE_VALUES or value.lower() in _FALSE_VALUES:
        return True, "bool"
    accepted = ", ".join(sorted(_TRUE_VALUES | _FALSE_VALUES))
    return False, f"expected bool ({accepted}), got {value!r}"


def validate_url(value, spec):
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https", "ftp") and parsed.netloc:
        return True, "url"
    return False, f"expected url, got {value!r}"


def validate_email(value, spec):
    if _EMAIL_RE.match(value):
        return True, "email"
    return False, f"expected email, got {value!r}"


def validate_enum(value, spec):
    values = spec.get("values")
    if not values:
        return False, "enum type requires a non-empty 'values' list"
    if value in values:
        return True, f"one of {values}"
    return False, f"expected one of {values}, got {value!r}"


def validate_regex(value, spec):
    pattern = spec.get("pattern")
    if not pattern:
        return False, "regex type requires a 'pattern'"
    if re.fullmatch(pattern, value):
        return True, f"matches /{pattern}/"
    return False, f"value {value!r} does not match /{pattern}/"


# Maps a schema 'type' name to its validator function.
VALIDATORS = {
    "string": validate_string,
    "int": validate_int,
    "float": validate_float,
    "bool": validate_bool,
    "url": validate_url,
    "email": validate_email,
    "enum": validate_enum,
    "regex": validate_regex,
}


def validate_value(value, spec):
    """Validate ``value`` against the given variable ``spec``.

    Returns ``(ok, detail)``.
    """
    type_name = spec.get("type", "string")
    validator = VALIDATORS.get(type_name)
    if validator is None:
        return False, f"unknown type {type_name!r}"
    return validator(value, spec)
