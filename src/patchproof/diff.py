from __future__ import annotations

import re
from pathlib import PurePosixPath

from .models import ChangedFile, ChangeSummary

DIFF_HEADER = re.compile(r"^diff --git a/(.+) b/(.+)$")
HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@")


def classify_path(path: str) -> tuple[str, ...]:
    normalized = path.replace("\\", "/").lower()
    name = PurePosixPath(normalized).name
    categories: set[str] = set()
    source_suffixes = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".c", ".h", ".cpp", ".hpp"}
    test_markers = {"test", "tests", "spec", "specs", "__tests__"}
    documentation_names = {"readme", "contributing", "changelog", "code_of_conduct", "security"}
    dependency_names = {"requirements.txt", "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "go.mod", "go.sum", "cargo.toml", "cargo.lock", "pyproject.toml"}
    config_names = {".gitignore", ".editorconfig", "dockerfile", "makefile", "tox.ini", "pytest.ini"}

    suffix = PurePosixPath(name).suffix
    if suffix in source_suffixes:
        categories.add("source")
    if any(part in test_markers for part in PurePosixPath(normalized).parts) or name.startswith("test_") or name.endswith("_test.py"):
        categories.add("tests")
    if suffix in {".md", ".rst", ".txt"} or PurePosixPath(name).stem in documentation_names:
        categories.add("documentation")
    if name in dependency_names:
        categories.add("dependencies")
    if name in config_names or name.startswith(".") or suffix in {".yml", ".yaml", ".toml", ".ini", ".json"}:
        categories.add("configuration")
    if normalized.startswith(("api/", "public/", "schema/")) or "/api/" in normalized:
        categories.add("public-interface")
    if not categories:
        categories.add("other")
    return tuple(sorted(categories))


def _parse_path(header: str) -> tuple[str, str]:
    match = DIFF_HEADER.match(header)
    if not match:
        raise ValueError("invalid diff header; expected 'diff --git a/path b/path'")
    return match.group(1), match.group(2)


def parse_unified_diff(text: str) -> ChangeSummary:
    lines = text.splitlines()
    changed: list[ChangedFile] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.startswith("diff --git "):
            index += 1
            continue
        old_path, new_path = _parse_path(line)
        path = new_path
        change_type = "modified"
        additions = 0
        deletions = 0
        index += 1
        while index < len(lines) and not lines[index].startswith("diff --git "):
            current = lines[index]
            if current.startswith("new file mode"):
                change_type = "added"
            elif current.startswith("deleted file mode"):
                change_type = "deleted"
                path = old_path
            elif current.startswith("rename from"):
                change_type = "renamed"
            elif current.startswith("Binary files"):
                change_type = "binary"
            elif current.startswith("+++ ") and current[4:] != "/dev/null":
                path = current[4:].removeprefix("b/")
            elif current.startswith("--- ") and current[4:] == "/dev/null":
                change_type = "added"
            elif HUNK_HEADER.match(current):
                index += 1
                while index < len(lines) and not lines[index].startswith("diff --git ") and not lines[index].startswith("@@ "):
                    hunk_line = lines[index]
                    if hunk_line.startswith("+") and not hunk_line.startswith("+++"):
                        additions += 1
                    elif hunk_line.startswith("-") and not hunk_line.startswith("---"):
                        deletions += 1
                    index += 1
                continue
            index += 1
        changed.append(
            ChangedFile(
                path=path,
                categories=classify_path(path),
                change_type=change_type,
                additions=additions,
                deletions=deletions,
            )
        )
    if not changed:
        raise ValueError("diff contains no file sections")
    categories = tuple(sorted({category for item in changed for category in item.categories}))
    risk_flags: set[str] = set()
    if "dependencies" in categories:
        risk_flags.add("dependency-change")
    if "public-interface" in categories:
        risk_flags.add("public-interface-change")
    if any(item.change_type in {"deleted", "binary"} for item in changed):
        risk_flags.add("destructive-or-binary-change")
    return ChangeSummary(tuple(sorted(changed, key=lambda item: item.path)), categories, tuple(sorted(risk_flags)))
