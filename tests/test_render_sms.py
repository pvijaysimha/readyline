import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import render_sms  # noqa: E402

TEMPLATES = json.loads((ROOT / "agent" / "sms-templates.json").read_text())
VALUES = {
    "BUSINESS_NAME": "Cascade Gutter Pros", "CALLER_NAME": "Dana R.", "CALLER_FIRST_NAME": "Dana",
    "CALLBACK_NUMBER": "(425) 555-0187", "CITY": "Kirkland", "JOB_DESCRIPTION": "gutters overflowing",
    "URGENCY": "this week", "STATUS": "Estimate booked Thu 9:00 AM", "CALL_LINK": "https://example.com/c/1",
    "BOOKING_LINE": "Your estimate is set for Thu Nov 6 at 9am", "BUSINESS_PHONE": "(425) 000-0000",
    "OWNER_NAME": "Mike", "JOB_SHORT": "gutter cleaning",
}


class RenderSmsTests(unittest.TestCase):
    def test_every_template_renders(self):
        for name, body in TEMPLATES.items():
            with self.subTest(template=name):
                text = render_sms.render(name, body, VALUES)
                self.assertNotIn("{{", text)

    def test_customer_templates_keep_opt_out(self):
        for name, body in TEMPLATES.items():
            if name not in render_sms.INTERNAL_TEMPLATES:
                with self.subTest(template=name):
                    self.assertIn(render_sms.OPT_OUT, body)

    def test_removed_opt_out_is_rejected(self):
        body = TEMPLATES["caller_confirmation"].replace(" Reply STOP to opt out.", "")
        with self.assertRaises(ValueError):
            render_sms.render("caller_confirmation", body, VALUES)

    def test_missing_value_is_rejected(self):
        with self.assertRaises(ValueError):
            render_sms.render("caller_confirmation", TEMPLATES["caller_confirmation"], {})

    def test_segments(self):
        self.assertEqual(render_sms.segments("a" * 160), 1)
        self.assertEqual(render_sms.segments("a" * 161), 2)
        self.assertEqual(render_sms.segments("a" * 70 + "€" * 45), 1)  # extended chars count double: 160
        self.assertEqual(render_sms.segments("a" * 70 + "€" * 46), 2)  # 162
        self.assertEqual(render_sms.segments("Thanks 🙂"), 1)
        self.assertEqual(render_sms.segments("🙂" * 40), 2)  # emoji forces the Unicode limits

    def test_cli(self):
        code = render_sms.main(["caller_confirmation", *[f"{k}={v}" for k, v in VALUES.items()]])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
