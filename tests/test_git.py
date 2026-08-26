from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from patchproof.git import GitError, get_unified_diff


class GitIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = Path(self.temp_dir.name)
        self._git("init", "-q")
        self._git("config", "user.name", "PatchProof Test")
        self._git("config", "user.email", "patchproof-test@example.invalid")
        (self.repository / "src.py").write_text("value = 1\n", encoding="utf-8")
        self._git("add", "src.py")
        self._git("commit", "-qm", "initial")
        self.base = self._git("rev-parse", "HEAD").stdout.strip()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _git(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.repository), *arguments],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_get_diff_between_explicit_revisions(self) -> None:
        (self.repository / "src.py").write_text("value = 2\n", encoding="utf-8")
        (self.repository / "tests.py").write_text("assert value == 2\n", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-qm", "add behavior and test")
        head = self._git("rev-parse", "HEAD").stdout.strip()

        diff = get_unified_diff(self.repository, self.base, head)

        self.assertIn("diff --git a/src.py b/src.py", diff)
        self.assertIn("diff --git a/tests.py b/tests.py", diff)
        self.assertIn("+value = 2", diff)

    def test_unknown_revision_is_rejected(self) -> None:
        with self.assertRaisesRegex(GitError, "unknown revision|bad revision|not found"):
            get_unified_diff(self.repository, self.base, "does-not-exist")

    def test_option_like_revision_is_rejected_before_git(self) -> None:
        with self.assertRaisesRegex(GitError, "must not start"):
            get_unified_diff(self.repository, "--help", self.base)

    def test_non_repository_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as empty:
            with self.assertRaisesRegex(GitError, "not inside a Git work tree"):
                get_unified_diff(Path(empty), self.base, self.base)


if __name__ == "__main__":
    unittest.main()
