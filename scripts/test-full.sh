#!/usr/bin/env bash
# Full suite: mirrors .github/workflows/ci.yml. Run before landing to main, or when touching
# brain/overlay/actions. See A-040/ADR-039. Full output never belongs in agent context — read
# the log path this prints if you need detail; quote only the tail printed on a FAIL below.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs/tests
LOG="logs/tests/full-$(date +%Y%m%d-%H%M%S).log"
failed=0

run() {
  local label=$1; shift
  local step_log; step_log=$(mktemp)
  "$@" >"$step_log" 2>&1
  local status=$?
  { echo "=== $label ==="; cat "$step_log"; } >>"$LOG"
  if ((status == 0)); then
    printf 'OK: %s\n' "$label"
  else
    failed=1
    printf 'FAIL: %s (last 30 lines)\n' "$label"
    tail -n 30 "$step_log"
  fi
  rm -f "$step_log"
  return "$status"
}

: >"$LOG"
run "doctor.sh --syntax" ./scripts/doctor.sh --syntax
run "python3 -m unittest discover -s tests" python3 -m unittest discover -s tests
run "shellcheck (scripts + skills)" bash -c 'find scripts skills -name "*.sh" -print0 | xargs -0 shellcheck'
run "node --check overlay/app.js" node --check overlay/app.js
run "node tests/overlay.test.cjs (5 suites)" node tests/overlay.test.cjs
run "check-test-coverage.py (no quiet suite omission)" python3 scripts/check-test-coverage.py
run "eval-status.py (docs/evals/cases.json)" python3 scripts/eval-status.py
run "stochastic-evals.py --validate (docs/evals/stochastic/)" python3 scripts/stochastic-evals.py --validate
run "check-control-plane.py (boundary + CODEOWNERS)" python3 scripts/check-control-plane.py

echo "Full log: $LOG"
if ((failed)); then
  echo "FULL SUITE FAILED. Do not paste this log into context — the tail above is already enough; quote it, don't re-fetch the whole file."
else
  echo "Full suite OK."
fi
exit "$failed"
