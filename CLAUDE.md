# ReadyLine: context for Claude

## The business

ReadyLine is a done-for-you missed-call service for Eastside Washington (Redmond, Kirkland, Bellevue, Sammamish, Woodinville, Bothell) owner-operators in gutter cleaning, roof-moss removal, pressure/soft washing and window cleaning who have no office staff. When the owner can't answer, calls forward to a voice-AI agent that collects job details, books an estimate or promises a callback, and texts the owner a summary. We also follow up on quiet quotes and send a monthly "jobs saved" report.

The owner of this project works on it about 10 hours a week. Keep things simple and cheap to run.

## Decisions already made (don't relitigate without a reason)

- **Price:** 14-day free pilot, then $500 setup + $199/month, month-to-month. One pilot tests $299.
- **Target:** owners NOT already on Jobber or Housecall Pro (those include their own AI receptionists).
- **Positioning:** sell "never lose a job to voicemail" plus follow-up and reporting, not "AI receptionist." Cheap direct apps (from ~$29–$49/month) set the price ceiling, so the value is the service.
- **Platform:** a white-label voice-AI platform (e.g. Trillet) rented, not built. We don't build telephony.
- **Name:** "ReadyLine" is a placeholder until checked against WA business records and trademarks.

## Legal guardrails (must stay in the code and scripts)

- Washington requires all-party consent to record calls (RCW 9.73.030). Every greeting must say "This call is recorded." `tools/render_agent.py` enforces this; keep that check.
- The agent must say it is an automated assistant and never pretend to be a person.
- AI-voice outbound calls need prior consent under the FCC's 2024 TCPA ruling. Only answer inbound calls; texts go only to people who contacted the business, max two quote follow-ups, always honor STOP.
- Caller data and recordings belong to the client. Never commit real client files or call logs (see `.gitignore`).
- No legal, insurance-claim or roof-safety advice from the agent.

## Repo layout

- `site/index.html`: landing page at https://pvijaysimha.github.io/readyline/, published by GitHub Pages via `.github/workflows/pages.yml`. Shows the demo line (425) 696-4103 (Retell, answers as the made-up Cascade Gutter Pros). The owner's own contact number is not on the site yet.
- `agent/voice-agent-prompt.txt`: prompt template with `{{PLACEHOLDERS}}`.
- `agent/sms-templates.json`: owner alert, caller confirmation, quote follow-ups.
- `examples/clients/cascade-gutter-pros.json`: demo client (made up).
- `tools/render_agent.py`: fills the template for a client; fails on missing values or a removed recording notice.
- `tools/import_calls.py`: converts a voice platform's CSV export to the call-log format using a JSON mapping (`examples/mappings/`); drops caller phone numbers.
- `tools/monthly_report.py`: turns a call log into the monthly report (Markdown or a self-contained HTML page).
- `tools/render_sms.py`: fills SMS templates; enforces the STOP opt-out line on customer texts and reports SMS segment count.
- `docs/`: setup checklist and pilot agreement draft (needs attorney review).
- Tests: `python -m unittest discover -s tests -v` (standard library only, Python 3.9+).

## Conventions

- Python standard library only unless there's a strong reason; keep scripts runnable with one command.
- Plain, short copy for contractors. No jargon like "AI-powered" in customer-facing text.
- Keep the site a single static HTML file with tokens for light and dark themes.

## Voice platform: Retell AI (chosen Nov 1, 2026)

- Workspace "ReadyLine"; demo agent "Cascade Gutter Pros (demo)", single-prompt type. Dashboard shows about $0.134/min with the current model.
- Demo number (425) 696-4103, inbound only, routed to the agent's V0 draft so edits apply immediately. Outbound is disabled; keep it that way (TCPA).
- Post-call extraction fields match the call-log columns: caller_name, callback_number, city, job_description, timing, category (lead/spam/sales), outcome (booked/callback/asked_human/hung_up_greeting).
- Call limits: ends after 37 s of silence, max call about 8 min.
- Not set up yet: SMS add-on ($20/month + $0.01/SMS in Retell), owner text via Zapier/Make, Calendly booking.

## Likely next steps

1. Add the owner's contact number to the site.
2. Write `examples/mappings/retell.json` once there's a real Retell call-history export to map.
3. Track prospects and pilots (currently in a spreadsheet outside this repo).

Done: generic call-log importer, HTML monthly report, SMS renderer with checks.
