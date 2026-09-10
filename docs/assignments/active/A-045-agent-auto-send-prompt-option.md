# A-045 — Agent manager: optional auto-send prompt into visible agent

- **Status:** queued
- **Area:** area:overlay (+ `brain/training.py` / agent launch helpers as needed)
- **parallel-ok:** YES
- **Recommended depth:** medium
- **Allowed paths (optional soft hint):** `overlay/agents.js`, `overlay/training.html`, `brain/training.py`, agent-window helpers, tests, docs/DECISIONS (ADR-043 follow-up), FEATURES/validation if user-visible
- **Forbidden paths (optional soft hint):** hidden/background agents; auto-approve desktop mutations; spending cloud without a visible window
- **Blocked-by:** A-044
- **Gate:** training-ux
- **Improvement:** none
- **Links:** Alex JARVIS room 2026-09-10 — “automatically send the prompt to the agent right away? (option that enables that somehow)” · supersedes the hard “never paste” half of ADR-043 **only** behind an explicit opt-in

## Goal
Add an **explicit opt-in** so Jarvis can, after preparing a handoff and opening/focusing the **visible** agent window, also deliver the prompt into that session (paste and/or submit — pick the safest mechanism that already works for that `kind`, document per backend).

Default remains today’s safe policy: prepare + focus only (ADR-043). The option must be obvious in Agent manager (per-delivery or sticky preference — choose and document), off by default, and never silently enabled.

Done for Alex: with the option on, “Start visibly now” / auto-advance can land the prompt in the agent without a manual paste; with it off, behavior is unchanged.

## Checklist
- [ ] Read ADR-043 + current advance/prepare paths; inventory what each `kind` (cursor/codex, claude, human, …) can safely receive
- [ ] Design opt-in UI + persistence (config.toml and/or Training preference); default **off**
- [ ] Implement delivery only to an already-visible / just-focused window; never create a hidden agent to “send”
- [ ] Submit vs paste-only: prefer paste-only if submit is unreliable; if submit is supported, gate it clearly (e.g. separate checkbox or mode)
- [ ] ADR follow-up amending ADR-043 (opt-in exception + safety invariants); PROGRESS; FEATURES/validation touch if needed
- [ ] Tests for “option off = no paste”; option on paths mocked/faked without real GUI when possible
- [ ] SESSION; QUEUE/INDEX → done; move brief to `done/`

## Out of scope
- Fixing Copy handoff (A-044) — land that first so blocked-by is real
- Auto-claiming assignments without the existing prepare/confirm flow
- Unattended cloud spend with no visible window

## Notes for the coding agent
ADR-043 currently forbids automatic paste/submit. This assignment is a **policy change behind a switch**, not a quiet behavior flip. If Hyprland automation (`wtype` / `ydotool` / toolkit paste) is required, document dependencies and failure modes in the ADR; degrade to copy+focus with a loud message when automation cannot run.
