"""Fill the voice-agent prompt template with one client's details.

Usage:
    python tools/render_agent.py examples/clients/cascade-gutter-pros.json
    python tools/render_agent.py client.json --out build/cascade-prompt.txt

Every {{PLACEHOLDER}} in the template must have a value in the client file;
missing values stop the script so a half-filled prompt never goes live.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "agent" / "voice-agent-prompt.txt"
PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

# The recording notice is required in Washington (all-party consent, RCW 9.73.030).
REQUIRED_PHRASE = "This call is recorded."


def placeholders(text: str) -> set[str]:
    return set(PLACEHOLDER.findall(text))


def render(template: str, values: dict[str, str]) -> str:
    missing = sorted(p for p in placeholders(template) if not str(values.get(p, "")).strip())
    if missing:
        raise ValueError("Missing values for: " + ", ".join(missing))
    out = PLACEHOLDER.sub(lambda m: str(values[m.group(1)]), template)
    if REQUIRED_PHRASE not in out:
        raise ValueError("The recording notice was removed from the greeting.")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("client", type=Path, help="Client JSON file")
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    parser.add_argument("--out", type=Path, help="Write here instead of printing")
    args = parser.parse_args(argv)

    values = json.loads(args.client.read_text(encoding="utf-8"))
    try:
        prompt = render(args.template.read_text(encoding="utf-8"), values)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(prompt, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
