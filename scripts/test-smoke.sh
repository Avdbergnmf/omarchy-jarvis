#!/usr/bin/env bash
# Fast, curated critical-path check. Default for small/docs changes; see A-040/ADR-039.
# Full output never belongs in agent context — the tail printed on a FAIL below is enough.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs/tests
LOG="logs/tests/smoke-$(date +%Y%m%d-%H%M%S).log"
failed=0

# One TestCase per named critical system (honesty/plan-approve, open-app, journal, training,
# validation) rather than the full ~158-case suite. Whole-class, not cherry-picked methods, so
# renaming a test method doesn't silently drop it from smoke.
PY_TARGETS=(
  tests.test_jarvis.JsonPlanTest
  tests.test_jarvis.ApprovalFlowTest
  tests.test_jarvis.OpenByNameTest
  tests.test_journal.JournalTest
  tests.test_training.TrainingTest
  tests.test_validation.ValidationTest
)

run() {
  local label=$1; shift
  local step_log; step_log=$(mktemp)
  "$@" >"$step_log" 2>&1
  local status=$?
  { echo "=== $label ==="; cat "$step_log"; } >>"$LOG"
  if ((status == 0)); then
    printf 'OK: %s — %s\n' "$label" "$(grep -E '^(Ran|OK)$|^Ran ' "$step_log" | tr '\n' ' ')"
  else
    failed=1
    printf 'FAIL: %s (last 30 lines)\n' "$label"
    tail -n 30 "$step_log"
  fi
  rm -f "$step_log"
  return "$status"
}

: >"$LOG"
run "python smoke (${#PY_TARGETS[@]} classes: ${PY_TARGETS[*]})" python3 -m unittest "${PY_TARGETS[@]}"
run "node tests/overlay.test.cjs (also runs training/validation/assignments/agents.test.cjs)" node tests/overlay.test.cjs

echo "Full log: $LOG"
if ((failed)); then
  echo "Smoke FAILED. Do not paste this log into context — the tail above is already enough. Run ./scripts/test-full.sh before landing to main."
else
  echo "Smoke OK. Run ./scripts/test-full.sh before landing to main or when touching brain/overlay/actions."
fi
exit "$failed"
