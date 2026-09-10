# A-044 — Agent manager: Copy handoff actually works

- **Status:** done
- **Area:** area:overlay (+ light brain only if handoff text is missing from the payload the UI can see)
- **parallel-ok:** YES
- **Recommended depth:** low
- **Allowed paths (optional soft hint):** `overlay/training.js`, `overlay/agents.js`, `overlay/training.html`, `overlay/training.css`, related tests, docs
- **Forbidden paths (optional soft hint):** auto-paste/submit into agent windows (that is A-045); rewriting Agent Monitor tiles (A-041)
- **Blocked-by:** none
- **Gate:** training-ux
- **Improvement:** none
- **Links:** Alex JARVIS room 2026-09-10 — “the copy handoff button doesnt work in the agent thing”

## Goal
In Training → Agent manager, **Copy handoff** reliably puts the prepared prompt on the clipboard (or gives a working fallback). Today `#train-copy` calls `navigator.clipboard.writeText` on `#train-handoff`; on the local Training window that often fails (permissions / non-secure context), and when `#train-result` is hidden or the textarea is empty the button feels dead.

Done for Alex: after prepare / auto-advance, one click copies the exact handoff he is about to paste; if the Clipboard API cannot write, the UI still makes a one-gesture copy possible (select + clear instructions, or an equivalent that works under Omarchy/Hyprland). Prefer also exposing Copy on the selected agent’s detail when `last_handoff` / prepared text exists so he does not have to hunt the “Prepared locally” panel.

## Checklist
- [x] Reproduce on Omarchy Training window: prepare a visible handoff, click Copy handoff — note failure mode (silent empty clipboard vs fallback select)
  — read-traced rather than live-clicked: `brain/server.py` binds a fixed port (7421) already
  held by the live Jarvis service another agent (Codex) is actively using for A-043, so a second
  instance against this worktree wasn't safe to stand up. Traced instead: `pollAgentAdvance`
  fills `#train-handoff` without re-syncing `#train-copy`'s hidden state, on top of the
  unguarded `navigator.clipboard.writeText` call — reproduced and pinned by the new unit tests
  (`tests/training.test.cjs`, `tests/agents.test.cjs`) rather than a manual click.
- [x] Fix copy path: robust Clipboard API usage + reliable fallback (see `overlay/latency.js` copy pattern); never claim success if write failed
- [x] Empty / hidden state: disable Copy or message clearly when there is no handoff text; surface the result panel when advance prepares text
- [ ] Optional UX: Copy control on agent detail for the current prepared / last handoff text — skipped: `last_handoff` is a handoff-file path, not the prepared text, and no endpoint serves that file's content to the client; out of scope for a low-depth fix.
- [x] Tests for the copy helper / empty-state behavior where practical
- [x] SESSION / PROGRESS; QUEUE/INDEX → done; move brief to `done/`

## Out of scope
- Pasting or submitting into Codex/Claude windows (A-045)
- Changing NEW_AGENT vs CONTINUE prompt content
- Assignments “Copy prompt” / Hand off panel switch unless the same bug is one shared helper — then fix once and reuse

## Notes for the coding agent
Start at `overlay/training.js` `#train-copy` listener and `pollAgentAdvance` filling `#train-handoff`. Training runs as a local file/app context — do not assume browser-secure clipboard permissions.
