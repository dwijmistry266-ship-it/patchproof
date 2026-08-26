from __future__ import annotations

import unittest

from patchproof.coverage import CoverageError, evaluate_coverage, parse_coverage_text
from patchproof.models import ChangeSummary
from patchproof.policy import DEFAULT_POLICY, evaluate_policy
from patchproof.report import build_report, render_markdown


VALID_COVERAGE = """<?xml version="1.0" encoding="UTF-8"?>
<coverage line-rate="0.875" branch-rate="0.75" lines-covered="35" lines-valid="40" branches-covered="12" branches-valid="16">
  <packages />
</coverage>
"""


class CoverageTests(unittest.TestCase):
    def test_parse_rates_and_counts(self) -> None:
        summary = parse_coverage_text(VALID_COVERAGE)
        self.assertAlmostEqual(summary.line_rate, 0.875)
        self.assertAlmostEqual(summary.branch_rate or 0, 0.75)
        self.assertEqual(summary.lines_covered, 35)
        self.assertEqual(summary.lines_valid, 40)
        self.assertEqual(summary.branches_covered, 12)
        self.assertEqual(summary.branches_valid, 16)

    def test_thresholds_pass(self) -> None:
        policy = {"coverage": {"minimum_line_rate": 0.80, "minimum_branch_rate": 0.70}}
        findings = evaluate_coverage(parse_coverage_text(VALID_COVERAGE), policy)
        self.assertEqual([item.status for item in findings], ["pass", "pass"])

    def test_line_threshold_failure_is_error(self) -> None:
        policy = {"coverage": {"minimum_line_rate": 0.90}}
        findings = evaluate_coverage(parse_coverage_text(VALID_COVERAGE), policy)
        self.assertEqual(findings[0].status, "error")
        self.assertIn("87.5%", findings[0].message)

    def test_missing_branch_rate_is_error_when_required(self) -> None:
        summary = parse_coverage_text("<coverage line-rate=\"0.9\" />")
        policy = {"coverage": {"minimum_branch_rate": 0.5}}
        findings = evaluate_coverage(summary, policy)
        self.assertEqual(findings[0].status, "error")
        self.assertIn("no branch rate", findings[0].message)

    def test_invalid_root_is_rejected(self) -> None:
        with self.assertRaisesRegex(CoverageError, "root must be"):
            parse_coverage_text("<report />")

    def test_invalid_rate_is_rejected(self) -> None:
        with self.assertRaisesRegex(CoverageError, "0 to 1"):
            parse_coverage_text("<coverage line-rate=\"1.2\" />")

    def test_invalid_threshold_is_rejected(self) -> None:
        with self.assertRaisesRegex(CoverageError, "minimum_line_rate"):
            evaluate_coverage(parse_coverage_text(VALID_COVERAGE), {"coverage": {"minimum_line_rate": 120}})

    def test_policy_includes_coverage_findings(self) -> None:
        summary = parse_coverage_text(VALID_COVERAGE)
        policy = {**DEFAULT_POLICY, "coverage": {"minimum_line_rate": 0.90}}
        findings = evaluate_policy(ChangeSummary((), (), ()), policy, coverage_summary=summary)
        self.assertEqual(findings[0].finding_id, "coverage-line-threshold")
        self.assertEqual(findings[0].status, "error")

    def test_coverage_renders_without_claiming_correctness(self) -> None:
        summary = parse_coverage_text(VALID_COVERAGE)
        report = build_report(ChangeSummary((), (), ()), (), (), coverage_summary=summary)
        markdown = render_markdown(report)
        self.assertIn("Coverage evidence", markdown)
        self.assertIn("Line coverage: **87.5%**", markdown)
        self.assertIn("does not prove correctness", markdown)


if __name__ == "__main__":
    unittest.main()
