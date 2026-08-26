from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from .models import TestSummary


class JUnitError(ValueError):
    """Raised when a JUnit XML report is invalid or unsupported."""


def _integer_attribute(element: ET.Element, name: str, default: int) -> int:
    raw = element.attrib.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise JUnitError(f"JUnit attribute '{name}' must be an integer") from exc
    if value < 0:
        raise JUnitError(f"JUnit attribute '{name}' cannot be negative")
    return value


def _duration_ms(element: ET.Element) -> int:
    raw = element.attrib.get("time")
    if raw is None or raw == "":
        return 0
    try:
        seconds = float(raw)
    except ValueError as exc:
        raise JUnitError("JUnit attribute 'time' must be a number of seconds") from exc
    if seconds < 0:
        raise JUnitError("JUnit attribute 'time' cannot be negative")
    return round(seconds * 1000)


def _suite_summary(suite: ET.Element) -> tuple[int, int, int, int, int]:
    testcases = [child for child in suite if child.tag.rsplit("}", 1)[-1] == "testcase"]
    tests = _integer_attribute(suite, "tests", len(testcases))
    failures = _integer_attribute(suite, "failures", sum(1 for case in testcases if any(child.tag.rsplit("}", 1)[-1] == "failure" for child in case)))
    errors = _integer_attribute(suite, "errors", sum(1 for case in testcases if any(child.tag.rsplit("}", 1)[-1] == "error" for child in case)))
    skipped = _integer_attribute(suite, "skipped", sum(1 for case in testcases if any(child.tag.rsplit("}", 1)[-1] == "skipped" for child in case)))
    duration = _duration_ms(suite)
    if "time" not in suite.attrib:
        duration = sum(_duration_ms(case) for case in testcases)
    return tests, failures, errors, skipped, duration


def parse_junit_text(text: str) -> TestSummary:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise JUnitError(f"invalid JUnit XML: {exc}") from exc
    root_name = root.tag.rsplit("}", 1)[-1]
    if root_name == "testsuites":
        suites = [child for child in root if child.tag.rsplit("}", 1)[-1] == "testsuite"]
    elif root_name == "testsuite":
        suites = [root]
    else:
        raise JUnitError("JUnit XML root must be 'testsuite' or 'testsuites'")
    if not suites:
        raise JUnitError("JUnit XML contains no test suites")
    totals = [0, 0, 0, 0, 0]
    for suite in suites:
        values = _suite_summary(suite)
        totals = [left + right for left, right in zip(totals, values)]
    return TestSummary(
        suites=len(suites),
        tests=totals[0],
        failures=totals[1],
        errors=totals[2],
        skipped=totals[3],
        duration_ms=totals[4],
    )


def parse_junit_file(path: Path) -> TestSummary:
    try:
        return parse_junit_text(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise JUnitError(f"JUnit report not found: {path}") from exc
    except UnicodeDecodeError as exc:
        raise JUnitError(f"JUnit report is not valid UTF-8: {path}") from exc
