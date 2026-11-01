import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import monthly_report  # noqa: E402
import render_agent  # noqa: E402


class RenderAgentTests(unittest.TestCase):
    def setUp(self):
        self.template = (ROOT / "agent" / "voice-agent-prompt.txt").read_text()
        self.client = json.loads((ROOT / "examples" / "clients" / "cascade-gutter-pros.json").read_text())

    def test_demo_client_fills_every_placeholder(self):
        out = render_agent.render(self.template, self.client)
        self.assertNotIn("{{", out)
        self.assertIn("Cascade Gutter Pros", out)

    def test_recording_notice_kept(self):
        out = render_agent.render(self.template, self.client)
        self.assertIn("This call is recorded.", out)

    def test_missing_value_is_rejected(self):
        client = dict(self.client, OWNER_NAME="")
        with self.assertRaises(ValueError):
            render_agent.render(self.template, client)

    def test_removed_recording_notice_is_rejected(self):
        template = self.template.replace("This call is recorded. ", "")
        with self.assertRaises(ValueError):
            render_agent.render(template, self.client)


class MonthlyReportTests(unittest.TestCase):
    def test_sample_log_counts(self):
        import csv
        with (ROOT / "examples" / "call_log_sample.csv").open(newline="") as f:
            s = monthly_report.summarize(list(csv.DictReader(f)))
        self.assertEqual(s.calls_answered, 8)
        self.assertEqual(s.real_leads, 6)
        self.assertEqual(s.booked, 3)
        self.assertEqual(s.asked_human, 1)
        self.assertEqual(s.hung_up, 2)
        self.assertEqual(s.followed_up, 2)
        self.assertEqual(s.jobs_won, 3)
        self.assertEqual(s.job_value, 1450)


if __name__ == "__main__":
    unittest.main()
