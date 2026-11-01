"""Build a client's monthly jobs-saved report from a call log CSV.

Usage:
    python tools/monthly_report.py examples/call_log_sample.csv \
        --client "Cascade Gutter Pros" --month "November 2026" --price 199

Call log columns (one row per call ReadyLine answered):
    date, caller_name, city, category, outcome, followed_up, job_won, job_value

    category:    lead | spam | sales
    outcome:     booked | callback | asked_human | hung_up_greeting
    followed_up: yes | no   (quote follow-up texts sent)
    job_won:     yes | no   (only jobs the owner confirmed)
    job_value:   dollars, blank if not won
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Summary:
    calls_answered: int = 0
    real_leads: int = 0
    booked: int = 0
    asked_human: int = 0
    hung_up: int = 0
    followed_up: int = 0
    jobs_won: int = 0
    job_value: float = 0.0


def _yes(value: str | None) -> bool:
    return (value or "").strip().lower() in {"yes", "y", "true", "1"}


def summarize(rows: list[dict[str, str]]) -> Summary:
    s = Summary()
    for row in rows:
        s.calls_answered += 1
        category = (row.get("category") or "").strip().lower()
        outcome = (row.get("outcome") or "").strip().lower()
        if category == "lead":
            s.real_leads += 1
        if outcome == "booked":
            s.booked += 1
        elif outcome == "asked_human":
            s.asked_human += 1
        elif outcome == "hung_up_greeting":
            s.hung_up += 1
        if _yes(row.get("followed_up")):
            s.followed_up += 1
        if _yes(row.get("job_won")):
            s.jobs_won += 1
            try:
                s.job_value += float((row.get("job_value") or "0").replace("$", "").replace(",", ""))
            except ValueError:
                pass
    return s


def render_markdown(s: Summary, client: str, month: str, price: float) -> str:
    lines = [
        f"# {client}: ReadyLine report for {month}",
        "",
        (f"ReadyLine answered **{s.calls_answered}** calls you couldn't pick up. "
         f"**{s.booked}** became booked estimates, and you confirmed **{s.jobs_won}** "
         f"jobs worth about **${s.job_value:,.0f}**. Your cost this month: **${price:,.0f}**."),
        "",
        "| Measure | This month |",
        "| --- | ---: |",
        f"| Calls answered by ReadyLine | {s.calls_answered} |",
        f"| Real leads (not spam or sales calls) | {s.real_leads} |",
        f"| Estimates booked | {s.booked} |",
        f"| Callers who asked for a human | {s.asked_human} |",
        f"| Callers who hung up during the greeting | {s.hung_up} |",
        f"| Quotes followed up | {s.followed_up} |",
        f"| Jobs you confirmed won | {s.jobs_won} |",
        f"| Approximate value of jobs won | ${s.job_value:,.0f} |",
        "",
        "**What we changed this month:** _fill in_",
        "",
        "**Next month:** _fill in_",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("call_log", type=Path)
    parser.add_argument("--client", required=True)
    parser.add_argument("--month", required=True)
    parser.add_argument("--price", type=float, default=199)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    with args.call_log.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    report = render_markdown(summarize(rows), args.client, args.month, args.price)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
