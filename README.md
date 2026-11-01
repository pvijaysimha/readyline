# ReadyLine

ReadyLine answers the calls Eastside gutter, roof-moss and exterior-cleaning owners miss, books the estimate, and texts them the details. This repo holds everything needed to run the service: the website, the voice-agent script, text templates, and tools for onboarding clients and reporting results.

> ReadyLine is a placeholder name. Check Washington business records and trademarks before using it.

## What's here

| Folder | What it is |
| --- | --- |
| `site/` | The landing page (`index.html`), deployed to GitHub Pages |
| `agent/` | Voice-agent prompt template and text-message templates |
| `examples/` | A demo client (Cascade Gutter Pros) and a sample call log |
| `tools/` | Scripts to fill in a client's prompt and build monthly reports |
| `docs/` | Setup checklist and pilot agreement draft |
| `tests/` | Checks that run on every push |

## Common tasks

Requires Python 3.9+; no extra packages.

**Make a voice-agent prompt for a new client**

1. Copy `examples/clients/cascade-gutter-pros.json` to a new file and fill in the client's details.
2. Run:
   ```
   python tools/render_agent.py path/to/client.json --out build/client-prompt.txt
   ```
3. Paste the output into the voice-AI platform's agent instructions.

The script refuses to run if any detail is missing or if the recording notice was removed from the greeting. Washington requires all parties' consent to record a call (RCW 9.73.030), so the notice must stay.

**Build a monthly report**

Export the month's calls from the platform into the CSV format shown in `examples/call_log_sample.csv`, then run:

```
python tools/monthly_report.py calls.csv --client "Client Name" --month "November 2026" --price 199 --out build/report.md
```

**Run the checks**

```
python -m unittest discover -s tests -v
```

## Website

`site/index.html` is a single static page. The GitHub Actions workflow in `.github/workflows/pages.yml` publishes it with GitHub Pages on every push to `main`. Turn Pages on once under the repo's **Settings → Pages → Source: GitHub Actions**.

Before sharing the site, replace the placeholder phone number `(425) 000-0000` in `site/index.html`.

## Not in this repo

- Phone numbers, voice-AI platform accounts, and API keys. Keep secrets out of git.
- Client call recordings or caller details. These belong to each client and stay in the platform.
