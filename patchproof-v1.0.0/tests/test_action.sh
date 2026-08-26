#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

python3 -m venv "$WORK/venv"
# shellcheck disable=SC1091
source "$WORK/venv/bin/activate"
python -m pip install --disable-pip-version-check --no-deps -e "$ROOT" >/dev/null

REPO="$WORK/repo"
mkdir -p "$REPO"
git -C "$REPO" init -q
git -C "$REPO" config user.name "PatchProof Test"
git -C "$REPO" config user.email "patchproof-test@example.invalid"
printf 'one\n' > "$REPO/example.txt"
git -C "$REPO" add example.txt
git -C "$REPO" commit -qm 'first'
printf 'two\n' >> "$REPO/example.txt"
git -C "$REPO" add example.txt
git -C "$REPO" commit -qm 'second'

export GITHUB_WORKSPACE="$REPO"
export PATCHPROOF_BASE_INPUT="$(git -C "$REPO" rev-parse HEAD~1)"
export PATCHPROOF_HEAD_INPUT="$(git -C "$REPO" rev-parse HEAD)"
export PATCHPROOF_DIFF_INPUT=""
export PATCHPROOF_CONFIG_INPUT=""
export PATCHPROOF_JUNIT_INPUT=""
export PATCHPROOF_COVERAGE_INPUT=""
export PATCHPROOF_OUTPUT_DIR="$WORK/report"
export PATCHPROOF_SKIP_COMMANDS="true"
export PATCHPROOF_EVENT_NAME="pull_request"
export PATCHPROOF_PR_BASE_SHA=""
export PATCHPROOF_EVENT_BEFORE=""
export PATCHPROOF_SHA="$PATCHPROOF_HEAD_INPUT"
export GITHUB_OUTPUT="$WORK/outputs"

"$ROOT/action/run.sh"
grep -Fq 'overall_status' "$WORK/report/report.json"
grep -Fq 'report-dir=' "$WORK/outputs"
test -f "$WORK/report/results.sarif"
printf '%s\n' 'action harness passed'
