from __future__ import annotations

import unittest

from patchproof.diff import parse_unified_diff


class DiffHardeningTests(unittest.TestCase):
    def test_quoted_path_with_spaces_is_preserved(self) -> None:
        diff = '''diff --git "a/src/my module.py" "b/src/my module.py"\nindex 1111111..2222222 100644\n--- "a/src/my module.py"\n+++ "b/src/my module.py"\n@@ -1 +1 @@\n-old()\n+new()\n'''
        summary = parse_unified_diff(diff)
        self.assertEqual(summary.changed_files[0].path, "src/my module.py")
        self.assertEqual(summary.changed_files[0].additions, 1)
        self.assertEqual(summary.changed_files[0].deletions, 1)

    def test_malformed_path_prefix_is_rejected(self) -> None:
        diff = "diff --git x/file.py b/file.py\n@@ -1 +1 @@\n-a\n+b\n"
        with self.assertRaisesRegex(ValueError, "must start with 'a/'"):
            parse_unified_diff(diff)

    def test_multiple_hunks_are_counted(self) -> None:
        diff = """diff --git a/src/app.py b/src/app.py
--- a/src/app.py
+++ b/src/app.py
@@ -1 +1 @@
-old-one
+new-one
@@ -10 +10 @@
-old-two
+new-two
"""
        summary = parse_unified_diff(diff)
        changed = summary.changed_files[0]
        self.assertEqual(changed.additions, 2)
        self.assertEqual(changed.deletions, 2)


if __name__ == "__main__":
    unittest.main()
