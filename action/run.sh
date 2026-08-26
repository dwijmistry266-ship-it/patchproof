#!/usr/bin/env bash
set -uo pipefail

args=(check --repo "$GITHUB_WORKSPACE" --output-dir "$PATCHPROOF_OUTPUT_DIR")

if [[ -n "${PATCHPROOF_DIFF_INPUT:-}" ]]; then
  args+=(--diff "$PATCHPROOF_DIFF_INPUT")
else
  base="${PATCHPROOF_BASE_INPUT:-}"
  head="${PATCHPROOF_HEAD_INPUT:-}"
  if [[ -z "$base" && "${PATCHPROOF_EVENT_NAME:-}" == "pull_request" ]]; then
    base="${PATCHPROOF_PR_BASE_SHA:-}"
  fi
  if [[ -z "$base" && "${PATCHPROOF_EVENT_NAME:-}" == "push" ]]; then
    base="${PATCHPROOF_EVENT_BEFORE:-}"
  fi
  if [[ -z "$head" ]]; then
    head="${PATCHPROOF_SHA:-}"
  fi
  if [[ -z "$base" || "$base" == "0000000000000000000000000000000000000000" ]]; then
    echo "PatchProof error: no usable base revision; set the action's base input or use a diff input." >&2
    exit 2
  fi
  if [[ -z "$head" ]]; then
    echo "PatchProof error: no usable head revision; set the action's head input or use a diff input." >&2
    exit 2
  fi
  args+=(--base "$base" --head "$head")
fi

[[ -n "${PATCHPROOF_CONFIG_INPUT:-}" ]] && args+=(--config "$PATCHPROOF_CONFIG_INPUT")
[[ -n "${PATCHPROOF_JUNIT_INPUT:-}" ]] && args+=(--junit "$PATCHPROOF_JUNIT_INPUT")
[[ -n "${PATCHPROOF_COVERAGE_INPUT:-}" ]] && args+=(--coverage "$PATCHPROOF_COVERAGE_INPUT")
[[ "${PATCHPROOF_SKIP_COMMANDS:-true}" == "true" ]] && args+=(--skip-commands)
args+=(--sarif "$PATCHPROOF_OUTPUT_DIR/results.sarif")

patchproof "${args[@]}"
code=$?

if [[ -f "$PATCHPROOF_OUTPUT_DIR/report.json" ]]; then
  status=$(python -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["overall_status"])' "$PATCHPROOF_OUTPUT_DIR/report.json")
  if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    echo "status=$status" >> "$GITHUB_OUTPUT"
    echo "report-dir=$PATCHPROOF_OUTPUT_DIR" >> "$GITHUB_OUTPUT"
  fi
fi

exit "$code"
