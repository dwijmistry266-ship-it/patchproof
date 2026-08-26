from __future__ import annotations

import json
import unittest

from patchproof.models import ChangeSummary, Finding
from patchproof.report import build_report
from patchproof.sarif import SARIF_SCHEMA, render_sarif


class SarifTests(unittest.TestCase):
    def test_rendered_log_has_required_top_level_fields(self) -> None:
        report = build_report(ChangeSummary((), (), ()), (
            Finding("tests-for-source", "error", "error", "Source changes do not include test changes.", ("src/app.py",)),
        ), ())
        payload = json.loads(render_sarif(report))
        self.assertEqual(payload["$schema"], SARIF_SCHEMA)
        self.assertEqual(payload["version"], "2.1.0")
        self.assertEqual(len(payload["runs"]), 1)
        self.assertEqual(payload["runs"][0]["tool"]["driver"]["name"], "PatchProof")

    def test_non_passing_finding_maps_to_rule_result_and_location(self) -> None:
        report = build_report(ChangeSummary((), (), ()), (
            Finding("tests-for-source", "error", "error", "Source changes do not include test changes.", ("./src/app.py",)),
            Finding("docs-for-public-interface", "warning", "warning", "Public-interface changes have no documentation change.", ("api.py",)),
            Finding("already-passed", "pass", "pass", "This must not become an alert.", ("ok.py",)),
        ), ())
        payload = json.loads(render_sarif(report))
        run = payload["runs"][0]
        self.assertEqual([rule["id"] for rule in run["tool"]["driver"]["rules"]], ["docs-for-public-interface", "tests-for-source"])
        self.assertEqual(len(run["results"]), 2)
        result = next(item for item in run["results"] if item["ruleId"] == "tests-for-source")
        self.assertEqual(result["level"], "error")
        self.assertEqual(result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"], "src/app.py")
        self.assertEqual(len(result["partialFingerprints"]["patchproof/v1"]), 32)

    def test_global_finding_is_retained_without_fake_file_location(self) -> None:
        report = build_report(ChangeSummary((), (), ()), (
            Finding("coverage-line-threshold", "error", "error", "Line coverage is below the required threshold."),
        ), ())
        result = json.loads(render_sarif(report))["runs"][0]["results"][0]
        self.assertNotIn("locations", result)
        self.assertTrue(result["properties"]["patchproof:global"])

    def test_rendering_is_deterministic(self) -> None:
        findings = (
            Finding("z-rule", "warning", "warning", "Zed", ("z.py",)),
            Finding("a-rule", "error", "error", "Alpha", ("a.py",)),
        )
        report = build_report(ChangeSummary((), (), ()), findings, ())
        self.assertEqual(render_sarif(report), render_sarif(report))


if __name__ == "__main__":
    unittest.main()
