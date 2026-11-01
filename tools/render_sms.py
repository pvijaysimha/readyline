"""Fill a text-message template and check it before it goes out.

Usage:
    python tools/render_sms.py caller_confirmation \
        BUSINESS_NAME="Cascade Gutter Pros" CALLER_FIRST_NAME=Dana \
        BOOKING_LINE="Your estimate is set for Thu Nov 6 at 9am" BUSINESS_PHONE="(425) 000-0000"

    python tools/render_sms.py --list

Checks:
- every {{PLACEHOLDER}} has a value
- texts to customers (everything except owner_alert) keep "Reply STOP to opt out"
- reports how many SMS segments the text uses, since long texts cost more
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "agent" / "sms-templates.json"
PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
OPT_OUT = "Reply STOP to opt out"
INTERNAL_TEMPLATES = {"owner_alert"}  # goes to the business owner, not a customer

# Characters in the standard SMS alphabet (GSM 03.38). Anything else forces
# the shorter Unicode limits.
GSM_BASIC = set(
    "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
    "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà"
)
GSM_EXTENDED = set("^{}\\[~]|€")


def segments(text: str) -> int:
    """Number of SMS segments a carrier will bill for this text."""
    if all(c in GSM_BASIC or c in GSM_EXTENDED for c in text):
        length = sum(2 if c in GSM_EXTENDED else 1 for c in text)
        single, multi = 160, 153
    else:
        length = len(text.encode("utf-16-le")) // 2
        single, multi = 70, 67
    if length <= single:
        return 1
    return math.ceil(length / multi)


def render(name: str, template: str, values: dict[str, str]) -> str:
    missing = sorted(p for p in set(PLACEHOLDER.findall(template)) if not str(values.get(p, "")).strip())
    if missing:
        raise ValueError("Missing values for: " + ", ".join(missing))
    text = PLACEHOLDER.sub(lambda m: str(values[m.group(1)]), template)
    if name not in INTERNAL_TEMPLATES and OPT_OUT not in text:
        raise ValueError(f"Customer texts must include '{OPT_OUT}'.")
    return text


def parse_pairs(pairs: list[str]) -> dict[str, str]:
    values = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Expected NAME=value, got '{pair}'")
        key, value = pair.split("=", 1)
        values[key.strip()] = value
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("template", nargs="?", help="Template name from agent/sms-templates.json")
    parser.add_argument("values", nargs="*", help="NAME=value pairs")
    parser.add_argument("--values-file", type=Path, help="JSON file of values (pairs override it)")
    parser.add_argument("--list", action="store_true", help="List template names")
    args = parser.parse_args(argv)

    templates = json.loads(TEMPLATES.read_text(encoding="utf-8"))
    if args.list or not args.template:
        for name, body in templates.items():
            fields = ", ".join(sorted(set(PLACEHOLDER.findall(body))))
            print(f"{name}: {fields}")
        return 0
    if args.template not in templates:
        print(f"Error: no template named '{args.template}'. Use --list.", file=sys.stderr)
        return 1

    try:
        values = json.loads(args.values_file.read_text(encoding="utf-8")) if args.values_file else {}
        values.update(parse_pairs(args.values))
        text = render(args.template, templates[args.template], values)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    print(text)
    n = segments(text)
    print(f"\n[{len(text)} characters, {n} SMS segment{'s' if n != 1 else ''}]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
