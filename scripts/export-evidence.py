#!/usr/bin/env python3
"""A-038: export one run's already-logged journal evidence as a bounded, redacted,
content-addressed bundle under $XDG_STATE_HOME/jarvis/evidence/ (default
~/.local/state/jarvis/evidence/). Read-only against the journal; never mutates a
run, never restarts the service, never claims anything is "backed up" — that is
true only once Alex selects and verifies a destination (see docs/evidence/README.md).

Usage:
  scripts/export-evidence.py <run_id> [--tier reference|summary|full] [--out DIR]

'full' includes the raw prompt/reply (still redacted of secrets) — opt-in only,
for when a human reviewing a regression genuinely needs the exact text.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'brain'))
import evidence  # noqa: E402
import server  # noqa: E402  (safe to import: no socket bind outside __main__)


def gather_fingerprint(prompt_rec):
    mode = prompt_rec.get('mode') or 'unknown'
    model = prompt_rec.get('model') or server.MODEL
    schema_obj = server.TOOLS_FOR_MODEL if mode == 'tools_run' else server.PLAN_SCHEMA
    system_prompt_path = ROOT / 'brain/system_prompt.md'
    system_prompt_hash = evidence.sha256_hex(system_prompt_path.read_text()) if system_prompt_path.exists() else None
    return evidence.fingerprint(
        jarvis_version=prompt_rec.get('jarvis_version') or server.VERSION,
        git_revision=prompt_rec.get('git_describe') or server.REVISION,
        planner_mode=mode,
        model=model,
        model_digest=evidence.ollama_model_digest(model),
        system_prompt_hash=system_prompt_hash,
        schema_hash=evidence.sha256_hex(json.dumps(schema_obj, sort_keys=True)),
        options={'temperature': 0, 'num_ctx': 8192},
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('run_id')
    parser.add_argument('--tier', choices=evidence.TIERS, default='summary')
    parser.add_argument('--out', help='Override the evidence directory (default: XDG state)')
    args = parser.parse_args(argv)

    phases = evidence.read_run_phases(server.LOGS, args.run_id)
    if not phases:
        print(f'No journal evidence found for run {args.run_id} under logs/runs/.', file=sys.stderr)
        return 1
    prompt_rec = next((p for p in phases if p.get('phase') == 'prompt'), {})
    fp = gather_fingerprint(prompt_rec)
    envelope = evidence.build_envelope(phases, fp, tier=args.tier)
    dest_dir = Path(args.out).expanduser() if args.out else evidence.EVIDENCE_DIR
    path, created = evidence.write_bundle(dest_dir, envelope)
    print(('Created' if created else 'Already durable (identical content)') + f': {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
