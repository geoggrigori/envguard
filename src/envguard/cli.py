"""Command-line interface for envguard."""

from __future__ import annotations

import argparse
import json
import os
import sys

from . import __version__
from .schema import (
    INVALID,
    MISSING,
    OK,
    SchemaError,
    load_schema,
    parse_env_file,
    validate_environment,
)

_HEADERS = ("VARIABLE", "STATUS", "DETAIL")


def render_table(results):
    """Render the results as an aligned text table."""
    rows = [_HEADERS]
    rows.extend((r["variable"], r["status"], r["detail"]) for r in results)

    widths = [max(len(row[i]) for row in rows) for i in range(3)]

    def fmt(row):
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip()

    lines = [fmt(_HEADERS)]
    lines.append("  ".join("-" * widths[i] for i in range(3)))
    lines.extend(fmt(row) for row in rows[1:])
    return "\n".join(lines)


def render_json(results):
    """Render the results as a machine-readable JSON array.

    Each entry has ``variable``, ``status`` (lowercased ``ok``/``missing``/
    ``invalid``) and ``detail``. Suitable for consumption in CI pipelines.
    """
    payload = [
        {
            "variable": r["variable"],
            "status": r["status"].lower(),
            "detail": r["detail"],
        }
        for r in results
    ]
    return json.dumps(payload, indent=2)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envguard",
        description="Validate environment variables against a declarative schema.",
    )
    parser.add_argument(
        "--schema",
        default="envguard.toml",
        help="path to the schema file (default: envguard.toml)",
    )
    parser.add_argument(
        "--env-file",
        default=None,
        help="optional .env file to load before reading the process environment",
    )
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="output format (default: table)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"envguard {__version__}",
    )
    return parser


def main(argv=None):
    """Entry point. Returns the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        schema = load_schema(args.schema)
    except SchemaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    # Build the environment view: process env overlaid on the .env file.
    environ = {}
    if args.env_file:
        try:
            environ.update(parse_env_file(args.env_file))
        except SchemaError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    environ.update(os.environ)

    results = validate_environment(schema, environ)

    failures = [r for r in results if r["status"] in (MISSING, INVALID)]

    if args.format == "json":
        print(render_json(results))
    else:
        print(render_table(results))
        ok_count = sum(1 for r in results if r["status"] == OK)
        print()
        print(f"{ok_count} ok, {len(failures)} failed, {len(results)} total")

    return 1 if failures else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
