from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

from patchproof.diff import parse_unified_diff
from patchproof.models import CommandResult
from patchproof.policy import DEFAULT_POLICY, evaluate_policy
from patchproof.report import build_report, render_json, render_markdown
from patchproof.runner import run_commands


SOURCE_WITH_TESTS = """diff --git a/src/app.py b/src/app.py
index 1111111..2222222 100644
--- a/src/app.py
+++ b/src/app.py
@@ -1,2 +1,3 @@
 def value():
-    return 1
+    return 2
+\n
diff --git a/tests/test_app.py b/tests/test_app.py
index 3333333..4444444 100644
--- a/tests/test_app.py
+++ b/tests/test_app.py
@@ -1,1 +1,2 @@
 assert True
+assert value() == 2
"""


class PatchProofTests(unittest.TestCase):
    def test_diff_parser_classifies_files_and_counts_changes(self) -> None:
        summary = parse_unified_diff(SOURCE_WITH_TESTS)
        self.assertEqual([item.path for item in summary.changed_files], ["src/app.py", "tests/test_app.py"])
        self.assertIn("source", summary.categories)
        self.assertIn("tests", summary.categories)
        self.assertEqual(summary.changed_files[0].additions, 2)
        self.assertEqual(summary.changed_files[0].deletions, 1)

    def test_dependency_change_without_lockfile_is_error(self) -> None:
        diff = """diff --git a/pyproject.toml b/pyproject.toml
index 111..222 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -1,1 +1,2 @@
 [project]
+dependencies = [\"requests\"]
"""
        summary = parse_unified_diff(diff)
        findings = evaluate_policy(summary, DEFAULT_POLICY)
        dependency_finding = next(item for item in findings if item.finding_id == "lockfile-for-dependency")
        self.assertEqual(dependency_finding.status, "error")

    def test_report_json_is_deterministic_without_runtime_metadata(self) -> None:
        summary = parse_unified_diff(SOURCE_WITH_TESTS)
        findings = evaluate_policy(summary, DEFAULT_POLICY)
        first = build_report(summary, findings, ())
        second = build_report(summary, findings, ())
        self.assertEqual(render_json(first), render_json(second))
        payload = json.loads(render_json(first))
        self.assertNotIn("runtime_metadata", payload)

    def test_markdown_contains_human_review_warning(self) -> None:
        summary = parse_unified_diff(SOURCE_WITH_TESTS)
        report = build_report(summary, evaluate_policy(summary, DEFAULT_POLICY), ())
        markdown = render_markdown(report)
        self.assertIn("Human review remains required", markdown)
        self.assertIn("src/app.py", markdown)

    def test_command_success_and_bounded_output(self) -> None:
        commands = [{"name": "python-ok", "command": [sys.executable, "-c", "print('ok')"]}]
        results = run_commands(commands, timeout_seconds=5, max_output_bytes=100)
        self.assertEqual(results[0].exit_code, 0)
        self.assertEqual(results[0].status, "pass")
        self.assertEqual(results[0].output.strip(), "ok")

    def test_command_timeout_is_error(self) -> None:
        commands = [{"name": "python-sleep", "command": [sys.executable, "-c", "import time; time.sleep(2)"]}]
        results = run_commands(commands, timeout_seconds=1, max_output_bytes=100)
        self.assertTrue(results[0].timed_out)
        self.assertEqual(results[0].status, "error")

    def test_command_output_is_truncated(self) -> None:
        commands = [{"name": "python-output", "command": [sys.executable, "-c", "print('x' * 1000)"]}]
        results = run_commands(commands, timeout_seconds=5, max_output_bytes=32)
        self.assertTrue(results[0].output_truncated)
        self.assertIn("output truncated", results[0].output)

    def test_malformed_diff_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_unified_diff("not a diff")

    def test_rename_and_binary_changes_raise_risk_flags(self) -> None:
        diff = """diff --git a/assets/logo.png b/assets/logo-new.png
similarity index 100%
rename from assets/logo.png
rename to assets/logo-new.png
Binary files a/assets/logo.png and b/assets/logo-new.png differ
"""
        summary = parse_unified_diff(diff)
        self.assertEqual(summary.changed_files[0].change_type, "binary")
        self.assertIn("destructive-or-binary-change", summary.risk_flags)

    def test_public_interface_without_docs_is_warning(self) -> None:
        diff = """diff --git a/api/v1/routes.py b/api/v1/routes.py
index 111..222 100644
--- a/api/v1/routes.py
+++ b/api/v1/routes.py
@@ -1,1 +1,2 @@
 def route():
+    return \"new\"
"""
        summary = parse_unified_diff(diff)
        findings = evaluate_policy(summary, DEFAULT_POLICY)
        finding = next(item for item in findings if item.finding_id == "docs-for-public-interface")
        self.assertEqual(finding.status, "warning")

    def test_dependency_change_with_lockfile_passes_rule(self) -> None:
        diff = """diff --git a/pyproject.toml b/pyproject.toml
index 111..222 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -1,1 +1,2 @@
 [project]
+dependencies = [\"requests\"]

diff --git a/poetry.lock b/poetry.lock
index 333..444 100644
--- a/poetry.lock
+++ b/poetry.lock
@@ -1,1 +1,2 @@
 [metadata]
+content-hash = \"updated\"
"""
        summary = parse_unified_diff(diff)
        findings = evaluate_policy(summary, DEFAULT_POLICY)
        finding = next(item for item in findings if item.finding_id == "lockfile-for-dependency")
        self.assertEqual(finding.status, "pass")


if __name__ == "__main__":
    unittest.main()
