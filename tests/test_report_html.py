import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import monthly_report  # noqa: E402


def sample_summary():
    with (ROOT / "examples" / "call_log_sample.csv").open(newline="") as f:
        return monthly_report.summarize(list(csv.DictReader(f)))


class HtmlReportTests(unittest.TestCase):
    def test_html_has_numbers_and_notes(self):
        page = monthly_report.render_html(sample_summary(), "Cascade Gutter Pros", "November 2026", 199,
                                          changes="Shortened the greeting", next_step="Add Saturday booking")
        self.assertIn("<!doctype html>", page)
        self.assertIn("Cascade Gutter Pros: November 2026", page)
        self.assertIn("$1,450", page)
        self.assertIn("Shortened the greeting", page)
        self.assertIn("prefers-color-scheme: dark", page)

    def test_html_escapes_client_name(self):
        page = monthly_report.render_html(sample_summary(), "Tom & Sons <Gutters>", "November 2026", 199)
        self.assertIn("Tom &amp; Sons &lt;Gutters&gt;", page)
        self.assertNotIn("<Gutters>", page)

    def test_markdown_uses_notes(self):
        md = monthly_report.render_markdown(sample_summary(), "C", "M", 199, changes="X", next_step="Y")
        self.assertIn("**What we changed this month:** X", md)
        self.assertIn("**Next month:** Y", md)

    def test_cli_writes_html(self):
        out = ROOT / "build" / "test-report.html"
        code = monthly_report.main([str(ROOT / "examples" / "call_log_sample.csv"), "--client", "C",
                                    "--month", "M", "--format", "html", "--out", str(out)])
        self.assertEqual(code, 0)
        self.assertTrue(out.read_text().startswith("<!doctype html>"))
        out.unlink()


if __name__ == "__main__":
    unittest.main()
