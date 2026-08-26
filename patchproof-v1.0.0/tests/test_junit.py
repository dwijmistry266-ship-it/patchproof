from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from patchproof.junit import JUnitError, parse_junit_file, parse_junit_text
from patchproof.models import ChangeSummary
from patchproof.report import build_report, render_markdown


VALID_REPORT = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="sample" time="0.45" tests="3" failures="1" errors="0" skipped="1">
  <testsuite name="unit" tests="2" failures="1" errors="0" skipped="1" time="0.40">
    <testcase classname="demo" name="passes" time="0.10" />
    <testcase classname="demo" name="skips" time="0.30"><skipped /></testcase>
  </testsuite>
  <testsuite name="integration">
    <testcase classname="demo" name="fails" time="0.05"><failure message="bad result" /></testcase>
  </testsuite>
</testsuites>
"""


class JUnitTests(unittest.TestCase):
    def test_parse_multiple_suites_and_attributes(self) -> None:
        summary = parse_junit_text(VALID_REPORT)
        self.assertEqual(summary.suites, 2)
        self.assertEqual(summary.tests, 3)
        self.assertEqual(summary.failures, 2)
        self.assertEqual(summary.errors, 0)
        self.assertEqual(summary.skipped, 1)
        self.assertEqual(summary.duration_ms, 450)
        self.assertEqual(summary.status, "error")

    def test_parse_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.xml"
            path.write_text(VALID_REPORT, encoding="utf-8")
            summary = parse_junit_file(path)
            self.assertEqual(summary.tests, 3)

    def test_single_suite_without_optional_attributes_counts_children(self) -> None:
        summary = parse_junit_text("""<testsuite name="unit"><testcase name="one" /><testcase name="two"><error /></testcase></testsuite>""")
        self.assertEqual(summary.suites, 1)
        self.assertEqual(summary.tests, 2)
        self.assertEqual(summary.errors, 1)
        self.assertEqual(summary.duration_ms, 0)

    def test_empty_testsuites_is_rejected(self) -> None:
        with self.assertRaisesRegex(JUnitError, "no test suites"):
            parse_junit_text("<testsuites />")

    def test_malformed_xml_is_rejected(self) -> None:
        with self.assertRaisesRegex(JUnitError, "invalid JUnit XML"):
            parse_junit_text("<testsuite>")

    def test_invalid_numeric_attribute_is_rejected(self) -> None:
        with self.assertRaisesRegex(JUnitError, "must be an integer"):
            parse_junit_text("<testsuite tests=\"many\" />")

    def test_negative_duration_is_rejected(self) -> None:
        with self.assertRaisesRegex(JUnitError, "cannot be negative"):
            parse_junit_text("<testsuite time=\"-0.1\"><testcase /></testsuite>")

    def test_test_summary_renders_in_report(self) -> None:
        summary = ChangeSummary((), (), ())
        test_summary = parse_junit_text(VALID_REPORT)
        report = build_report(summary, (), (), test_summary=test_summary)
        markdown = render_markdown(report)
        self.assertIn("Test-result evidence", markdown)
        self.assertIn("Failures: **2**", markdown)
        self.assertEqual(report.overall_status, "error")


if __name__ == "__main__":
    unittest.main()
