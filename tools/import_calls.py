"""Convert a voice platform's call export into ReadyLine's call-log format.

Every platform exports calls differently, so a small JSON mapping file says
which of its columns and values mean what. Once mapped, the output works with
tools/monthly_report.py.

Usage:
    python tools/import_calls.py export.csv --mapping examples/mappings/generic-export.json \
        --out build/calls-2026-11.csv

Mapping file keys:
    columns       ReadyLine column -> platform column name
    date_format   optional strptime format of the platform's date column
    values        ReadyLine column -> {platform value: ReadyLine value} (case-insensitive)
    defaults      ReadyLine column -> value used when the platform has no data

Owners confirm jobs won after the fact, so job_won and job_value usually start
as defaults and get filled in by hand before the monthly report.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

FIELDS = ["date", "caller_name", "city", "category", "outcome", "followed_up", "job_won", "job_value"]
ALLOWED = {
    "category": {"lead", "spam", "sales"},
    "outcome": {"booked", "callback", "asked_human", "hung_up_greeting"},
    "followed_up": {"yes", "no"},
    "job_won": {"yes", "no"},
}


def convert_row(row: dict[str, str], mapping: dict) -> tuple[dict[str, str], list[str]]:
    """Return one ReadyLine row and a list of problems found in it."""
    columns = mapping.get("columns", {})
    values = {k: {str(a).strip().lower(): b for a, b in v.items()} for k, v in mapping.get("values", {}).items()}
    defaults = mapping.get("defaults", {})
    out: dict[str, str] = {}
    problems: list[str] = []

    for field in FIELDS:
        source = columns.get(field)
        raw = (row.get(source) or "").strip() if source else ""
        if not raw:
            out[field] = str(defaults.get(field, ""))
            continue
        if field in values:
            mapped = values[field].get(raw.lower())
            if mapped is None:
                problems.append(f"{field}: unknown value '{raw}'")
                out[field] = str(defaults.get(field, ""))
                continue
            raw = mapped
        if field == "date" and mapping.get("date_format"):
            try:
                raw = datetime.strptime(raw, mapping["date_format"]).date().isoformat()
            except ValueError:
                problems.append(f"date: can't read '{raw}'")
        out[field] = raw

    for field, allowed in ALLOWED.items():
        if out[field] and out[field].lower() not in allowed:
            problems.append(f"{field}: '{out[field]}' is not one of {sorted(allowed)}")
    return out, problems


def convert(rows: list[dict[str, str]], mapping: dict) -> tuple[list[dict[str, str]], list[str]]:
    converted, problems = [], []
    for i, row in enumerate(rows, start=2):  # row 1 is the header
        out, row_problems = convert_row(row, mapping)
        converted.append(out)
        problems.extend(f"row {i}: {p}" for p in row_problems)
    return converted, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("export", type=Path, help="Platform's CSV export")
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="Write here instead of printing")
    args = parser.parse_args(argv)

    mapping = json.loads(args.mapping.read_text(encoding="utf-8"))
    with args.export.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    converted, problems = convert(rows, mapping)

    target = args.out.open("w", newline="", encoding="utf-8") if args.out else sys.stdout
    try:
        writer = csv.DictWriter(target, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(converted)
    finally:
        if args.out:
            target.close()

    for p in problems:
        print(f"Warning: {p}", file=sys.stderr)
    if args.out:
        print(f"Wrote {len(converted)} calls to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
