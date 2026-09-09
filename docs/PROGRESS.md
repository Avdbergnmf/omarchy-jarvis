# Progress log

## 2026-09-09 — Handoff scaffold
- Repo created private on GitHub; docs + layout seeded by Firsty for Astra 6.
- Host facts captured in `docs/ASTRA_HANDOFF.md` and `docs/HOST.md`.
- Not yet implemented: overlay, brain loop, actions, example skills runtime tests.

## 2026-09-09 — Implementation started
- Cloned into `/home/omarchy/Work/omarchy-jarvis`; read ASTRA_HANDOFF end-to-end and all required docs.
- Live catalog confirms SUPER+SHIFT+J is free; Outlook/WhatsApp URLs match the handoff.
- Ollama binary exists but neither its server nor a user unit is present. Creating a localhost user service next.
- Hyprland exposes Lua callbacks in `hyprctl binds`; the printed catalog has descriptions/chords but no command column. Critical bindings will use explicit reviewed action mappings.
- Desktop/session-bus access requires execution outside the workspace sandbox; initial read-only probes succeeded there.

### Host implementation and first integration pass
- Installed/enabled localhost Ollama user service; downloaded qwen2.5:3b (1.9 GB). Ollama hello succeeded.
- Added JSON-output actions and both executable skills. Live scratch test passed with a disposable foot window; SUPER+S toggle and SUPER+M Outlook binding tests passed.
- First planning pass exposed Brave window-class matching at Google Calendar; fixed matching to app hostname in the actual webapp class. Subsequent CLI run verified all four apps on workspace 3.
- Notification native `invokeLast` action opened floating 875×600 foot running `tail -n 100 -F logs/runs/console-smoke.log` (PID 13469 at test time).
- Jarvis service installed, SUPER+SHIFT+J installed with backup; Hyprland reload/configerrors clean. Overlay observed floating, centered, size 520×150.
- Fourteen regression tests, Python/shell syntax, JS syntax and both skill metadata validators passed.
- First model-driven demos were NOT accepted: native tool calling performed incomplete planning and duplicate scratch actions. Switched to structured JSON plans (ADR-009); rerunning stronger integration checks.
- Browser automation connector exposes no browsers/native apps on this host; UI verification uses live Hyprland state and native action invocation. Physical mouse-click/keyboard input cannot be synthesized through that unavailable connector.

### Acceptance verification
- Structured planner live pass: hello `6cc5d559-9237-44de-8922-0f8dc4ee149c`; planning `63a13e91-4dab-4548-8756-c9ba0e9a2bcb`; scratch-and-mail `7cb4e67b-7dad-451e-8cb9-2a5f81587753`.
- Planning evidence: all four actual Brave webapp classes verified on fresh workspace **4**. Scratch evidence: disposable window `0x5626b3f4e340` verified in `special:scratchpad`. Runtime evidence is in ignored `logs/demo-evidence.json` and timestamped run logs.
- `scripts/verify-host.py` now passes: exact Host/token/Origin rejection; invalid input rejection; repeated single-instance overlay open/close; 520×150 floating rules; close endpoint used by Escape; native notification action; `tail -F` continues reading after filename replacement.
- Chromium repeat-launch class mismatch resolved with unique app route + observed-class match (ADR-013). Earlier unsuccessful launch attempts are documented above; no process-killing workaround remains in normal toggle behavior.
- `scripts/doctor.sh` exits **0** on the live host. Both user services are active; Hyprland configuration validates cleanly.
- Local suite: **19 Python tests**, shell/Python syntax, extensionless action/console compile checks, JS syntax, overlay submit/completion/Escape behavior, and both SKILL.md metadata validators pass.
- M4 CLI approval stub tested in an isolated temporary repository: unconfirmed install rejected; modified draft invalidates digest; approved exact bytes install and execute; overwrite rejected.
- GitHub is verified PRIVATE. M0–M4 milestones already existed; added missing M5 milestone and created workstream issues **#1–#5**. M4 remains open for UI confirmation and installed-skill discovery.
- Limitation: browser/native UI connector exposes no surfaces. Native notification invocation is tested through the same Omarchy action used by a click; physical key/mouse input itself was not automated. Some webapps show login screens; no credentials or messages were entered.
- Final overlay-focus demo also passed: hello `b136caa7-934b-4b01-9c61-340066f19590`, planning `1163b05a-6e5c-4dcf-b1db-2143e3157aa5`, scratch-and-mail `7c8b5739-e76c-407d-b752-c6aa3cec320f`. The scratch test opened the real overlay before submission and verified that the original disposable window, not the overlay, moved. The test then closed only its disposable window. Final catalog contains `SUPER SHIFT + J → Jarvis overlay`; both services report enabled.
