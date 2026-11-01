"""Build a client's monthly jobs-saved report from a call log CSV.

Usage:
    python tools/monthly_report.py examples/call_log_sample.csv \
        --client "Cascade Gutter Pros" --month "November 2026" --price 199

    # Same report as a page you can send to the client:
    python tools/monthly_report.py calls.csv --client "..." --month "..." \
        --format html --changes "Shortened the greeting" --next "Add Saturday booking" \
        --out build/report.html

Call log columns (one row per call ReadyLine answered):
    date, caller_name, city, category, outcome, followed_up, job_won, job_value

    category:    lead | spam | sales
    outcome:     booked | callback | asked_human | hung_up_greeting
    followed_up: yes | no   (quote follow-up texts sent)
    job_won:     yes | no   (only jobs the owner confirmed)
    job_value:   dollars, blank if not won

tools/import_calls.py converts a voice platform's export into this format.
"""
from __future__ import annotations

import argparse
import csv
import html
from dataclasses import dataclass
from pathlib import Path

PLACEHOLDER_NOTE = "_fill in_"


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


def measures(s: Summary) -> list[tuple[str, str]]:
    return [
        ("Calls answered by ReadyLine", str(s.calls_answered)),
        ("Real leads (not spam or sales calls)", str(s.real_leads)),
        ("Estimates booked", str(s.booked)),
        ("Callers who asked for a human", str(s.asked_human)),
        ("Callers who hung up during the greeting", str(s.hung_up)),
        ("Quotes followed up", str(s.followed_up)),
        ("Jobs you confirmed won", str(s.jobs_won)),
        ("Approximate value of jobs won", f"${s.job_value:,.0f}"),
    ]


def headline(s: Summary, price: float) -> str:
    return (f"ReadyLine answered {s.calls_answered} calls you couldn't pick up. "
            f"{s.booked} became booked estimates, and you confirmed {s.jobs_won} "
            f"jobs worth about ${s.job_value:,.0f}. Your cost this month: ${price:,.0f}.")


def render_markdown(s: Summary, client: str, month: str, price: float,
                    changes: str = PLACEHOLDER_NOTE, next_step: str = PLACEHOLDER_NOTE) -> str:
    lines = [
        f"# {client}: ReadyLine report for {month}",
        "",
        (f"ReadyLine answered **{s.calls_answered}** calls you couldn't pick up. "
         f"**{s.booked}** became booked estimates, and you confirmed **{s.jobs_won}** "
         f"jobs worth about **${s.job_value:,.0f}**. Your cost this month: **${price:,.0f}**."),
        "",
        "| Measure | This month |",
        "| --- | ---: |",
        *[f"| {label} | {value} |" for label, value in measures(s)],
        "",
        f"**What we changed this month:** {changes}",
        "",
        f"**Next month:** {next_step}",
        "",
    ]
    return "\n".join(lines)


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root {{ --bg:#eef1ef; --surface:#fff; --ink:#18211f; --muted:#55625e; --line:#cfd8d4; --brand:#1d5a4c; --hivis:#f2b51d; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#111816; --surface:#18221f; --ink:#e7eeeb; --muted:#9db0aa; --line:#2c3a36; --brand:#5cc2a8; --hivis:#f5c444; color-scheme: dark; }} }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font: 16px/1.55 "Segoe UI", Helvetica, Arial, sans-serif; }}
main {{ max-width: 640px; margin: 0 auto; padding: 32px max(16px, env(safe-area-inset-left, 0px)) 48px; display:flex; flex-direction:column; gap:22px; }}
.mark {{ font-weight: 800; letter-spacing: .04em; text-transform: uppercase; display:flex; align-items:center; gap:8px; color: var(--muted); font-size: .85rem; }}
.mark span {{ width:10px; height:10px; border-radius:50%; background:var(--hivis); }}
h1 {{ margin:0; font-size: 1.7rem; line-height: 1.15; text-wrap: balance; }}
.lede {{ margin:0; font-size: 1.1rem; }}
.stats {{ display:grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }}
.stat {{ background:var(--surface); border:1px solid var(--line); border-radius:8px; padding:14px; }}
.stat b {{ display:block; font-size: 1.8rem; line-height:1.1; color: var(--brand); font-variant-numeric: tabular-nums; }}
.stat small {{ color: var(--muted); }}
table {{ width:100%; border-collapse: collapse; background:var(--surface); border:1px solid var(--line); border-radius:8px; overflow:hidden; font-variant-numeric: tabular-nums; }}
td {{ padding: 10px 14px; border-bottom: 1px solid var(--line); }}
td.v {{ text-align: right; font-weight: 600; }}
tr:last-child td {{ border-bottom: 0; }}
.note h2 {{ margin: 0 0 4px; font-size: 1rem; }}
.note p {{ margin: 0; color: var(--muted); }}
footer {{ color: var(--muted); font-size: .85rem; }}
@media (max-width: 480px) {{ .stats {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<main>
  <div class="mark"><span></span>ReadyLine monthly report</div>
  <h1>{client}: {month}</h1>
  <p class="lede">{lede}</p>
  <div class="stats">
    <div class="stat"><b>{calls}</b><small>calls answered for you</small></div>
    <div class="stat"><b>{booked}</b><small>estimates booked</small></div>
    <div class="stat"><b>{won}</b><small>jobs you confirmed won</small></div>
  </div>
  <table>
    <tbody>
{rows}
    </tbody>
  </table>
  <div class="note"><h2>What we changed this month</h2><p>{changes}</p></div>
  <div class="note"><h2>Next month</h2><p>{next_step}</p></div>
  <footer>Questions about this report? Reply to the text or email it came with.</footer>
</main>
</body>
</html>
"""


def render_html(s: Summary, client: str, month: str, price: float,
                changes: str = "Nothing changed this month.", next_step: str = "Keep tuning based on your calls.") -> str:
    e = html.escape
    rows = "\n".join(f"      <tr><td>{e(label)}</td><td class=\"v\">{e(value)}</td></tr>" for label, value in measures(s))
    return HTML_TEMPLATE.format(
        title=e(f"{client} report, {month}"),
        client=e(client), month=e(month), lede=e(headline(s, price)),
        calls=s.calls_answered, booked=s.booked, won=s.jobs_won,
        rows=rows, changes=e(changes), next_step=e(next_step),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("call_log", type=Path)
    parser.add_argument("--client", required=True)
    parser.add_argument("--month", required=True)
    parser.add_argument("--price", type=float, default=199)
    parser.add_argument("--format", choices=["markdown", "html"], default="markdown")
    parser.add_argument("--changes", help="What you changed in the client's setup this month")
    parser.add_argument("--next", dest="next_step", help="What you'll improve next month")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    with args.call_log.open(newline="", encoding="utf-8") as f:
        summary = summarize(list(csv.DictReader(f)))

    notes = {k: v for k, v in {"changes": args.changes, "next_step": args.next_step}.items() if v}
    if args.format == "html":
        report = render_html(summary, args.client, args.month, args.price, **notes)
    else:
        report = render_markdown(summary, args.client, args.month, args.price, **notes)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
