import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import import_calls  # noqa: E402
import monthly_report  # noqa: E402


def load_sample():
    mapping = json.loads((ROOT / "examples" / "mappings" / "generic-export.json").read_text())
    with (ROOT / "examples" / "platform_export_sample.csv").open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    return rows, mapping


class ImportCallsTests(unittest.TestCase):
    def test_sample_export_converts_cleanly(self):
        rows, mapping = load_sample()
        out, problems = import_calls.convert(rows, mapping)
        self.assertEqual(problems, [])
        self.assertEqual(len(out), 5)
        first = out[0]
        self.assertEqual(first["date"], "2026-11-03")
        self.assertEqual(first["category"], "lead")
        self.assertEqual(first["outcome"], "booked")
        self.assertEqual(first["job_won"], "no")

    def test_caller_phone_number_not_copied(self):
        rows, mapping = load_sample()
        out, _ = import_calls.convert(rows, mapping)
        self.assertNotIn("(425) 555-0187", json.dumps(out))

    def test_unknown_value_is_reported(self):
        rows, mapping = load_sample()
        rows[0]["Disposition"] = "Voicemail Left"
        _, problems = import_calls.convert(rows, mapping)
        self.assertTrue(any("unknown value 'Voicemail Left'" in p for p in problems))

    def test_output_feeds_monthly_report(self):
        rows, mapping = load_sample()
        out, _ = import_calls.convert(rows, mapping)
        s = monthly_report.summarize(out)
        self.assertEqual(s.calls_answered, 5)
        self.assertEqual(s.real_leads, 3)
        self.assertEqual(s.booked, 2)
        self.assertEqual(s.hung_up, 1)


if __name__ == "__main__":
    unittest.main()
