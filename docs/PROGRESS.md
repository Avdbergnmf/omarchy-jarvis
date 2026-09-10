# Progress log

## 2026-09-09 — Handoff scaffold
- Repo created private on GitHub; docs + layout seeded by Firsty for Astra 6.
- Host facts captured in `docs/passes/archive/ASTRA_HANDOFF.md` and `docs/HOST.md`.
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
- Delivery PR: #6. First CI run passed Python tests but ShellCheck flagged an unchecked `cd` and nested-shell quoting in doctor.sh. Fixed both directly (explicit failed-cd exit; model check as a shell function), then reran CI.
- CI is green on implementation commit `53b20e2`: https://github.com/Avdbergnmf/omarchy-jarvis/actions/runs/34366901098 (PR) and https://github.com/Avdbergnmf/omarchy-jarvis/actions/runs/34366896608 (push). ShellCheck, 19 Python tests, syntax checks and overlay JS behavior all pass. The indirect model-check function triggered one additional ShellCheck diagnostic; calling it directly resolved it.
- Final host cleanup closed only Jarvis disposable test windows; the four planning webapps remain together on workspace **2**. Final service code is active; both services remain enabled. Release delivery is through PR #6 with milestone tags `v0.0.1`, `v0.1.0`, `v0.2.0`, `v0.3.0`; M4/#5 remains follow-up scope.

## 2026-09-09 — Transparency & control pass (`docs/passes/active/CLAUDE_TRANSPARENCY_PASS.md`)

**Before:** the overlay posted a prompt, showed "Thinking…", then polled straight to a final reply. Tool calls (workspace changes, webapp launches, scratchpad moves) had already run by the time the user saw anything — no visibility into the plan and no way to stop it.

**After:** every prompt now goes through **plan → wait → execute**. `POST /v1/run` plans only; if the plan has actions it returns `status=awaiting_approval` with the proposed `plan` and nothing has touched the desktop yet. The overlay shows the plan as a checklist with **Run**/**Cancel** buttons (Run auto-focused so Enter confirms); only `POST /v1/runs/<id>/approve` executes it, and `POST /v1/runs/<id>/deny` cancels with zero side effects. While executing, `GET /v1/runs/<id>` streams a `steps[]` list (tool → running/done/error + result summary) that the overlay renders live. Chitchat with no actions still replies immediately, skipping approval. See ADR-014/ADR-015.

New/changed surfaces:
- `brain/server.py`: `plan_and_maybe_run` / `execute_plan` (JSON planner) and `plan_tools_run` / `execute_tools_plan` (opt-in `JARVIS_PLANNER=tools` loop) replace the old immediate-execute functions. New endpoints `POST /v1/runs/<id>/approve`, `/deny`, `/console`. `GET /health` adds `ollama: ok|fail` and `approval_mode`. Config loaded once from `~/.config/jarvis/config.toml` (`approval_mode`, `show_notifications`); stale `awaiting_approval` runs (>900s) auto-deny so a closed overlay can't wedge the single-run lock.
- `overlay/`: plan checklist, live step list, Run/Cancel buttons, footer (model · ollama status · approval-mode warning), and an **always-visible Open console** button — present from first paint, disabled only until a run id exists, and re-enabled pointing at the last run (via `localStorage`) even after the overlay window is closed and reopened. Escape denies any pending plan, then closes.
- Overlay window grew **520×150 → 640×460** (`scripts/toggle-overlay.py`, `scripts/install-hotkey.py`, re-applied to the live `~/.config/hypr/bindings.lua` on this host, `scripts/verify-host.py`).
- `scripts/demo-test.py` now drives the API end-to-end: approves/denies through `/approve` and `/deny` instead of expecting immediate execution; added a deny-first pass on the planning prompt to prove no side effects.

### How to demo
1. `SUPER + SHIFT + J`, type "toggle scratchpad", press Enter → plan panel shows `scratch_toggle` with Run/Cancel; nothing has happened yet.
2. Press Enter again (focus is on Run) → overlay closes, action runs, `Completed: scratch toggle.` appears in the run log; Esc/Cancel instead → `Cancelled — no actions were run.` and the scratchpad is untouched.
3. Click **Open console** (or reopen the overlay after closing it — the button stays enabled for the last run) → `jarvis-console <run_id>` opens the live log, including the `plan`/`tool-call`/`stdout` lines.
4. `curl http://127.0.0.1:7421/health` shows `model`, `ollama`, and `approval_mode` for the footer.

### Acceptance verification (live on this host, `try-omarchy`)
1. "Say hello…" → `status=done` immediately, `plan.actions` empty, no hypr/webapp calls in the run log.
2. "toggle scratchpad" via `wtype` into the real overlay window: plan panel appeared with `scratch_toggle`, Run focused; scratchpad state (`hyprctl clients`) was unchanged for ~45s until Enter was pressed on Run; only then did `hl.dsp.workspace.toggle_special("scratchpad")` run and the run log recorded `Completed: scratch toggle.`. Screenshots taken with `grim` confirm the rendered plan/Run/Cancel UI and the always-visible Open console button (grayed pre-run, enabled once a run id exists, still enabled after closing/reopening the overlay).
3. `scripts/demo-test.py`: denied "open my planning in a new workspace" first — asserted no new workspace and no new webapp windows — then approved the same prompt, which placed all four apps on a fresh workspace as before.
4. During the approved planning/scratch-and-mail runs, `GET /v1/runs/<id>` `steps[]` updated per tool call; `POST /v1/runs/<id>/console` (what the Open-console button calls) opened a live `jarvis-console` window tailing the same run log.
5. `./scripts/doctor.sh` (live) and `./scripts/doctor.sh --syntax` both exit 0 after the change; `python3 -m unittest discover -s tests` — 31 tests pass (12 new `ApprovalFlowTest` cases covering awaiting/approve/deny/expiry/config modes); `node tests/overlay.test.cjs` passes against the rewritten overlay UI; `scripts/verify-host.py` passes (640×460 float size).
6. Evidence: run ids and screenshots above; full run logs under (git-ignored) `logs/runs/`; `logs/demo-evidence.json` regenerated by the updated `scripts/demo-test.py`.

### CI bug found and fixed: busy-lock leak on a logging failure
First push of this pass hung PR #7's `python3 -m unittest discover` step for 15+ minutes on GitHub's runner (twice, on independent fresh runners) while passing instantly (0.33s) locally every time. Root cause, found by pulling the in-progress job's raw logs via `gh api .../jobs/<id>/logs`: `ApprovalFlowTest.test_action_plan_awaits_approval_by_default`'s cleanup call `server.handle_deny(rid)` hit the real (unmocked) `log()` function, which tried to write to `logs/runs/<id>.log` — a directory that only exists locally because the live service had already created it during earlier manual testing, but doesn't exist in a fresh CI checkout (`logs/` is gitignored). The write raised `FileNotFoundError`, and since `handle_deny`/`expire_stale` called `log()` then `release_busy()` with no `finally`, the exception skipped the release and left the process-wide `BUSY` lock permanently held — so the very next test's `server.BUSY.acquire()` blocked forever, and stdout being block-buffered (non-tty) meant nothing more ever printed to explain why.

This was a real production robustness gap, not just a test artifact: any run-log write failure (disk full, `logs/` deleted mid-run, permissions) could have wedged the single-run lock for every future request until a service restart — exactly the kind of failure this transparency pass is supposed to prevent. Fixed by wrapping every `log()`/`announce()` call that precedes a `release_busy()` in `try/finally` (`handle_deny`, `expire_stale`, and the chitchat/exception branches of `plan_and_maybe_run`/`plan_tools_run`), and added `setUpModule()` in `tests/test_jarvis.py` to create `logs/runs/` up front, mirroring the precondition `server.py`'s own startup already guarantees in production. Verified by copying the checkout to `/tmp` with `logs/` and `.git` removed and an isolated `HOME`/`PATH`, confirming the suite still passed — CI is now green in ~10s (matching pre-pass baseline).

## 2026-09-09 — Self-improve loop pass (`docs/passes/active/CLAUDE_SELF_IMPROVE_PASS.md`)

**Before:** a bad experience or a feature idea just went into the chat and was gone. No way to hand a miss or a request to a colder, smarter (paid) agent with enough context to act without the original conversation; nothing tracked, nothing routed.

**After:** `/report …` or "you messed up …" starts a **bug intake**; `/feature …` or "I wish it could …" starts a **feature intake**. Both gather an automatic context pack (last run's plan/approval/log tail; a live `hyprctl` snapshot and binding-catalog hits, only when the seed text looks window/binding-related), then ask up to 3 fixed clarifying questions one at a time (`status=awaiting_answer`, new `POST /v1/runs/<id>/answer`; reply `"skip"` any time to file with what's there). The finished draft (title + full templated body) is shown in the **same** plan/approve UI as every other action — nothing is filed until **Run** — and `report_bug`/`report_feature` call `gh issue create` plus write a local mirror under `docs/backlog/{bugs,features}/` and append a row to `docs/backlog/INDEX.md`. `/backlog` lists open items (GitHub + the local index); `/dispatch <issue> to <agent>` writes a paste-ready `docs/backlog/handoffs/issue-<n>-<agent>.md` and **never contacts or spends credits on another agent** — no real-send hook exists in this pass, by design. See ADR-016.

New/changed surfaces:
- `brain/server.py`: deterministic intent routing in `POST /v1/run` (`detect_intake`, `BACKLOG_SLASH`, `DISPATCH_SLASH`) runs **before** the JSON/tool planner, so bug/feature drafting never depends on the local 3B model (`report_bug`/`report_feature` are excluded from `PLAN_SCHEMA`/`TOOLS_FOR_MODEL` via `LLM_EXCLUDED_TOOLS` — the model literally cannot select them). `start_intake`/`handle_answer`/`finalize_intake` drive the new `awaiting_answer` state; `commit_plan` (factored out of the old `plan_and_maybe_run`) is now the single place a finished plan decides auto-run vs. awaiting approval, reused by intake, `/backlog`, and `/dispatch`. `expire_stale`/`handle_deny` now also cover `awaiting_answer` so an abandoned Q&A can't wedge the busy lock or leave Escape unable to cancel it.
- `actions/core.py`: `redact` moved here from `server.py` (single source of truth, imported back) and extended with `sk-`/`gh[ops]_`-shaped token patterns. New `report_record`/`list_backlog`/`prepare_handoff`/`ensure_labels`/`fill_template`/`slugify`/`backlog_slug`/`index_append` plus four new thin CLI wrappers (`report_bug`, `report_feature`, `list_backlog`, `prepare_handoff`), all JSON-stdout/`--dry-run` like every existing action.
- `docs/templates/{ISSUE_BUG,ISSUE_FEATURE,HANDOFF_AGENT}.md` + `docs/backlog/{README,INDEX,bugs/,features/,handoffs/}` — the backlog skeleton and routing guide the doc asked for.
- Two new reviewed example skills, `skills/examples/{report-last-failure,add-feature-request}`: scripted, non-interactive shortcuts (last-run-log excerpt / CLI-supplied text straight into `report_bug`/`report_feature`, no Q&A) demonstrating composition for a cold agent; deliberately **not** added to `run_skill`'s model-facing enum in `brain/tools.json`, so the model can't select them — CLI/doctor use only.
- `overlay/`: new `#qa` section (question + answer input + Skip button, `POST /v1/runs/<id>/answer`) and a `#draft-preview` box (title + scrollable full body) inside the existing plan panel, shown whenever a plan carries a `draft`. Escape now denies on `awaiting_answer` too, not just `awaiting_approval`.
- `scripts/doctor.sh`: dry-run checks for all four new actions and both new skills, plus `gh auth status`.

### Real bug found and fixed while filing the first live issue
The very first live approve of a `report_bug` plan failed with `gh failed: could not add label: 'jarvis-reported' not found` — `gh issue create --label` errors outright if a label doesn't exist yet in the target repo, and `jarvis-reported`/`backlog` are new, Jarvis-specific labels this repo never had. Fixed by having `report_record` call `gh label create --force` (idempotent create-or-update, safe to call every time) for the four labels (`bug`, `jarvis-reported`, `enhancement`, `backlog`) immediately before `gh issue create`, on the real (non-dry) path only. Covered by a new unit test (`test_ensure_labels_is_idempotent_create_or_update`) and by re-asserting `ensure_labels` is called once per real `report_record` call.

### Acceptance verification (live on this host, `try-omarchy`)
1. **Deny path, no side effects:** `/report …` (natural-language trigger) → 3 questions answered → full templated draft shown (`draft.title`/`draft.body`, including a real `hyprctl clients/workspaces` snapshot since the seed mentioned "scratchpad") → **Deny** → `status=denied`, nothing created.
2. **Real filing:** `/report jarvis-smoke: …` → skipped Q&A → **Run** → real `gh issue create` succeeded after the label fix above → **issue [#8](https://github.com/Avdbergnmf/omarchy-jarvis/issues/8)**, labeled `bug`, `jarvis-reported` (then manually labeled `jarvis-smoke` and closed as smoke-test evidence, per the source doc's "close/label jarvis-smoke if needed") — local mirror `docs/backlog/bugs/bug-jarvis-smoke-live-verification-issue-for-the-s.md` and an `INDEX.md` row were written in the same call.
3. **Feature intake:** "I wish it could remember my last workspace…" → correctly routed to `report_feature` (not `report_bug`), difficulty guessed `M` → denied (no second real issue filed; the identical `report_record` code path filing to `docs/backlog/features/` is covered by `BacklogActionsTest`).
4. **`/backlog`** → `status=done`, `list_backlog` ran for real (`gh issue list` + the local `INDEX.md` — correctly empty of open issues once #8 was closed).
5. **`/dispatch 8 to claude-code`** → `status=done`, real `gh issue view` + wrote `docs/backlog/handoffs/issue-8-claude-code.md` with the full context pack, acceptance criteria, forbidden actions, and an explicit "does not contact or spend credits on claude-code itself" line. No agent was contacted.
6. `./scripts/doctor.sh` (live) and `--syntax` both exit 0; `python3 -m unittest discover -s tests` — **49 tests** pass (18 new: intent detection, the Q&A state machine including skip and expiry, redaction including token-shaped secrets, template filling, `ensure_labels`, `execute_plan` skipping `restore_target` for non-desktop tools, `report_bug`/`report_feature` excluded from the model-facing planner); `node tests/overlay.test.cjs` passes against the rewritten overlay (plan/approve/Escape/console **plus** the new Q&A → draft-preview flow); `shellcheck` clean on all shell scripts including the two new skills.
7. Live filing above used the deployed `jarvis.service` (restarted mid-pass to pick up the code), not a bypass — confirming the whole path runs the same way a real user pressing **Run** in the overlay would trigger it.

One live hiccup unrelated to this pass's code: the very first approve attempt got a transient `gh` DNS/connectivity error (`error connecting to api.github.com`); a `systemd-run --user` probe confirmed outbound access from a transient user-scope unit works fine, and the retry succeeded — noted here in case it recurs, but not treated as a bug in this pass.

## 2026-09-09 — Agent entrypoint, pass lifecycle, multi-agent seams & run journal (`docs/passes/active/CLAUDE_AGENT_ENTRYPOINT_PASS.md`)

**Before:** a cold agent had no single front door — `AGENTS.md` mixed invariants with workflow instructions, three separate `CLAUDE_*_PASS.md`/`PROMPT_*` files sat loose in `docs/` with no way to tell which were still current, and nothing said which files two agents could safely touch at once. Run evidence was `logs/runs/<id>.log` free text — fine for a live `tail -F` but not something an agent could `jq` for "what was asked, what happened, does anything look off," and per-tool argv/stdout noise lived at the same verbosity as the events that actually mattered.

**After:** `START.md` is the new front door (first lines say: read this fully before anything else) — job modes (fix issues / implement a pass / feature from backlog / explore-debug), the Issue Loop (`./scripts/agent-status.sh` + `gh issue list`), area-scoped parallel work (`area:{overlay,brain,actions,skills,docs}`, `parallel-ok` + explicit `Allowed paths:`/`Forbidden paths:`, `single-writer` default for brain/control-plane), the pass/handoff active→archive→INDEX lifecycle, and a docs map. `AGENTS.md` is slimmed to durable invariants only, pointing at `START.md`. The three loose pass docs plus `ASTRA_HANDOFF.md` moved into `docs/passes/{active,archive}/` with an `INDEX.md`; `docs/backlog/handoffs/` got the same active/archive/INDEX treatment (issue #8's handoff moved to `archive/`, marked done). Run evidence is now a structured **journal**: `brain/journal.py` writes four bounded JSONL records per run (`prompt → process → done → eval`) to `logs/journal/CURRENT.jsonl`, each with `jarvis_version` (`VERSION` file) and a startup-cached `git_describe`; `evaluate()` is a local, synchronous, rules-only check (no cloud call, no subprocess, no desktop snapshot) that conservatively flags even successful runs `suspicious` since a tool's return code alone can't prove the desktop actually changed. Module/internal noise is `debug`-only (`log_level` in `~/.config/jarvis/config.toml`, default `info`) to `logs/debug/<run_id>.jsonl`; `GET /v1/runs` polling stays silent either way. See ADR-017/ADR-018.

New/changed surfaces:
- `START.md` (new), `AGENTS.md` (slimmed from ~55 to ~21 lines, invariants only), `README.md` ("Agents and debugging" pointing at `START.md`/`docs/LOGGING.md`).
- `docs/passes/{README,INDEX,active/,archive/}` and `docs/backlog/handoffs/{README,INDEX,active/,archive/}`; `actions/core.py`'s `prepare_handoff` now writes to `handoffs/active/` and archives+re-indexes any prior handoff for the same issue+agent instead of silently overwriting it. Every stale reference to the old flat `docs/CLAUDE_*_PASS.md`/`docs/PROMPT_*`/`docs/ASTRA_HANDOFF.md`/`docs/backlog/handoffs/issue-*.md` paths (ADR-016, `docs/backlog/README.md`, both handoff/issue templates, `docs/PROGRESS.md` itself) was updated to the new locations rather than left dangling.
- `brain/journal.py` (new): `Journal.write`/`.append`, `clean()` (redaction + bounds: 1,500-char strings, 12-entry lists, 30-key dicts, nested-JSON-string redaction), `evaluate()`. `brain/server.py`: `journal_event()` called on prompt (`do_POST /v1/run`), process (repurposing the existing `log(run_id,'plan',...)` call site), and done+eval (from `release_busy()`, covering every terminal path — chat, deny, timeout/expire, error, executed, and the opt-in tools-loop chat branch — in one place); `log()` now only writes debug-level module detail (gated on `CONFIG['log_level']`), no longer the primary run log. `docs/LOGGING.md` (new): full schema, eval rules, debug opt-in, version-reset procedure, `jq` recipes.
- `scripts/agent-status.py`/`.sh` (new): read-only issue-by-area overview, `parallel-ok`/`single-writer`/path-overlap warnings (conservative prefix comparison, human-review-only), active passes/handoffs, last 5 journal `run_id`s (bounded tail read, not a full-file scan), a doctor one-liner. `.github/ISSUE_TEMPLATE/workstream.md` gained an "Area and ownership" section (label choice, `Allowed paths:`/`Forbidden paths:`) and a "Run evidence" section (`run_id`, journal path/archive, `jarvis_version`, expected vs actual). Both issue templates (`ISSUE_BUG.md`/`ISSUE_FEATURE.md`) gained the same area-ownership block; `HANDOFF_AGENT.md` gained a "Read `START.md` first" line, a run-evidence/ownership section, and an archive-on-done reminder.
- `VERSION` (new, `0.4.1`). New GitHub labels on the real repo: `area:overlay`, `area:brain`, `area:actions`, `area:skills`, `area:docs`, `parallel-ok`, `single-writer`.
- ADR-017 (front door/pass lifecycle/parallel seams) and ADR-018 (versioned journal, debug-only internals) in `docs/DECISIONS.md`.
- `tests/test_journal.py` (new): journal rotation on a `VERSION` change (old file archived byte-for-byte, console projection matches), redaction/bounds (including nested-JSON-string secrets and a `sk-`-shaped token), all four evaluate() flag branches (`mismatch`/`partial`/`suspicious`/`None` on deny), all four journal phases present with real `jarvis_version`/`ts`/`run_id` across six terminal outcomes (chat, deny, timeout, error, an executed tool, and the tools-loop chat branch) with **no** subprocess/model call on the eval path itself, a journal-write-failure still releases the busy lock, and `log_level=debug` opt-in writes to `logs/debug/` while `info` doesn't. `tests/test_jarvis.py`'s `setUpModule`/`tearDownModule` now redirect `LOGS` to a temp directory for the whole suite (previously wrote into the real repo's `logs/`) and clean it up afterward.

### Acceptance verification (live on this host, `try-omarchy`)
1. `./scripts/agent-status.sh` (live, real repo): grouped open issues by area, listed active passes/handoffs, showed recent journal `run_id`s, printed the doctor one-liner — matches the "cold agent → START → agent-status → issues" acceptance flow.
2. Live journal demo: a real "say hello please" prompt through the deployed `jarvis.service` produced exactly four JSONL records — `prompt → process → done → eval` — each carrying the real `jarvis_version` (`0.4.1`) and `git_describe` (`v0.0.1-4-gac6a675-dirty`, correctly `-dirty` on this uncommitted tree) and matching timestamps; the same four lines landed in `logs/runs/<run_id>.log` unchanged (console projection). A second live run (`/backlog`, approved for real) showed a populated `steps`/`happened` payload and `eval.flag = "suspicious"` — the documented conservative-on-success behavior, since a successful tool call alone doesn't prove the desktop changed. Both `jq` recipes from `docs/LOGGING.md` ran successfully against the real `logs/journal/CURRENT.jsonl`.
3. `python3 -m unittest discover -s tests` — **56 tests** pass (7 new in `test_journal.py` beyond the 49 from the self-improve pass); `node tests/overlay.test.cjs`, `./scripts/doctor.sh --syntax`, `shellcheck` on every shell script (now including `scripts/agent-status.sh`), and `./scripts/doctor.sh` (live) all pass/exit 0 after restarting `jarvis.service` to load the journal-wired code.
4. `docs/passes/INDEX.md`/`docs/backlog/handoffs/INDEX.md` reviewed by hand: every `active/` entry has a matching file, every `archive/` entry is marked `done`/`superseded`, nothing archived is referenced as a live instruction anywhere in `START.md`/`AGENTS.md`.

### Note on this session's provenance
This pass's implementation (this dated section, ADR-017/018 polish, and this verification pass aside) was already complete and uncommitted in the shared `~/Work/omarchy-jarvis` checkout when this session picked it up — the working tree was found mid-checkout on branch `codex/agent-entrypoint-journal`, one commit ahead of the self-improve pass, with no separate git history to show whose keystrokes produced it. A peer Claude session sharing this same checkout confirmed it wasn't theirs and that the content matches this brief exactly; all of it passed the full test/lint/live-doctor suite as found, needing only this PROGRESS entry, an ADR formatting fix (ADR-017/018 were missing the standard bold Context/Decision/Consequences labels other ADRs use), and the live journal/agent-status demo above before commit. Flagged to Alex: this checkout has **no worktree isolation** between concurrent agent sessions — a second untracked pass brief (`docs/passes/active/CLAUDE_AGENT_EFFICIENCY.md`) appeared in the same directory mid-verification, from a session outside this one; it was left untouched.

## 2026-09-09 — Assignment queue (desk process)

- Added `docs/assignments/` with QUEUE, TEMPLATE, authoring README, active A-001..A-003, and Alex paste prompts (CONTINUE / PARALLEL / NEW_AGENT).
- START/AGENTS/README link the queue; `docs/SESSION.md` stub; `scripts/assignment-status.sh`.
- Docs only — no Jarvis runtime code changes.

## 2026-09-09 — Post-merge housekeeping

- Audited main (`7b26886`): transparency / self-improve / entrypoint+journal / assignments present; tests green.
- Archived completed pass briefs + prompts under `docs/passes/archive/`; INDEX now shows active empty.
- Marked assignments A-001..A-003 **done** (moved to `docs/assignments/done/`); QUEUE empty for new asks.
- Left **M4** (skill confirm UI) open as intentional product backlog, not silently closed.

## 2026-09-09 — A-004: overlay stays open through execution (follow-along visibility)

**Before:** pressing Run closed the overlay window immediately — `restore_target()` ran at the *start* of `execute_plan`/`execute_tools_plan` and closed every `is_overlay` client before a single step executed or the overlay's own poller could render anything, then re-focused the pre-overlay window (immediately re-focused past by each action's own dispatch on completion). Net effect: the overlay vanishes the instant Run is pressed, the screen flashes to the old window, and the real result (up to ~30s later for a newly-launched webapp) appears with nothing visible in between — matching Alex's report of "a flash then back to nowhere" and wanting a "chance to see what it's doing."

**After:** `restore_target()` still focuses the pre-overlay target before an action runs (still required for `scratch_move_here`/current-window-dependent bindings) but no longer closes any window. The overlay stays open through planning, awaiting-approval, live step execution and the terminal reply; the user dismisses it with **Esc** or by pressing the hotkey again (`toggle-overlay.py`'s existing single-instance close-if-focused/refocus-if-not logic, unchanged). See ADR-019.

- `brain/server.py::restore_target`: removed the `dispatch('closewindow', …)` loop over `is_overlay` clients; kept the `focuswindow` dispatch and the "original window disappeared" failure.
- `tests/test_jarvis.py`: `test_restore_target_focuses_without_closing_overlay` (exactly one `focuswindow` dispatch, no close, given an overlay client is present) and `test_restore_target_noop_without_a_target`.
- `README.md`: one-liner that the overlay stays open and how to dismiss it.
- Chitchat (`commit_plan`'s zero-action branch) and denied plans (`handle_deny`) were already unaffected either way — neither ever called `restore_target`.

### Verification
- `python3 -m unittest discover -s tests` — **58 tests** pass (2 new). `node tests/overlay.test.cjs`, `./scripts/doctor.sh --syntax`, `shellcheck` all pass.
- Live: restarted `jarvis.service` to load the change; `./scripts/doctor.sh` (live) exits 0.
- Not yet done in this session: a live approve-and-watch demo confirming the overlay visibly stays on screen through a real `open_webapp`/workspace-switch run (this host's browser/native UI automation connector exposes no surfaces per earlier passes' documented limitation — verification here is via `hyprctl` state and the targeted unit tests above, not a screenshot). Left as the next-action note in `docs/SESSION.md` for whoever resumes, in case a different verification path becomes available.

## 2026-09-09 — A-005: post-run feedback (+/neutral/−)

**Before:** after a run finished, the only way to flag a problem was to type a fresh `/report`/`/feature` (or a natural-language trigger), which re-derives context from "whatever ran most recently" rather than the run the user actually meant.

**After:** the overlay shows 👍/🤔/👎 once a run reaches `done`/`error` (hidden again once rated). 👍 is a one-line journal record. 🤔 additionally appends to a local-only `logs/feedback/needs-review.jsonl` — never a GitHub issue, so it can't spam the tracker. 👎 reuses the existing deterministic bug-intake flow (`start_intake`) but now with an explicit `source_run_id` so the filed issue's context (plan, approval, log excerpt) always describes the *rated* run, not an adjacency guess. New endpoint `POST /v1/runs/<id>/feedback`; `handle_feedback` in `brain/server.py`. See ADR-020, `docs/LOGGING.md` (new optional `feedback` journal phase).

- `brain/server.py`: refactored `last_run_info` → `run_info(run_id, run)` (pure) + `previous_run_id(current_id)` (the old ordering logic); `gather_context`/`start_intake` gained `source_run_id`. Added `FEEDBACK_RATINGS`, `record_needs_review`, `handle_feedback`, and the `/feedback` HTTP route.
- `overlay/{index.html,app.js,style.css}`: `#feedback` section with 👍/🤔/👎; hidden during any non-terminal status or once `result.feedback` is set; 👎 hands its returned `run_id` to the existing `poll()` loop so the intake Q&A appears like any other run.
- `tests/test_jarvis.py::FeedbackTest` (7 new: good/neutral/bad happy paths, one-rating-per-run guard, unknown-rating guard, non-terminal-run guard, busy-run-refuses-bad-rating, and that the bad-path context references the *rated* run specifically, not the previous one). `tests/overlay.test.cjs` extended for button visibility/hide and the thumbs-down → intake handoff (using direct `post`/`render`/`get` calls for the bad-path assertion, not the real button click, since this test file's synchronous `setTimeout` mock would otherwise recurse `poll()` forever against a `run_id` that never leaves `awaiting_answer` — same hazard already flagged in the file's own comment for the pre-existing `qa-run` scenario).
- README one-liner.

### Verification
- `python3 -m unittest discover -s tests` — **65 tests** pass (7 new). `node tests/overlay.test.cjs` PASS. `./scripts/doctor.sh --syntax` OK.
- Live: restarted `jarvis.service` to load the change. `./scripts/doctor.sh` (live) all OK, brain listening.
- Live end-to-end over the real HTTP API (real Ollama planning, real `gh`-free paths): started a chitchat run ("say hi back to me, nothing else") → `done` → `POST .../feedback {rating:good}` → 200, `feedback:"good"`; repeat on same run → 400 "Feedback already recorded". Second chitchat run → `done` → `{rating:neutral}` → 200; confirmed `logs/feedback/needs-review.jsonl` got a redacted `{ts,run_id,prompt,reply}` line and no `gh issue` was touched. Real approved action run (`toggle scratchpad`, which the planner resolved to the `scratch-and-mail` skill this time — a live planner quirk, not part of this change) → `done` → `{rating:bad}` → 202 with a fresh `run_id` → polled that run to `awaiting_answer`, reply `"What did you expect to happen?"` (confirms `source_run_id` context attachment reached `start_intake` for real, and stayed correct even with other test runs happening around it — no naive "most recent run" mix-up) → denied the intake to leave the service idle. A **denied** run correctly returns 409 ("not in a terminal state") when rated — denied runs never executed anything, so a rating doesn't apply. Confirmed `logs/journal/CURRENT.jsonl` has one `feedback` record per rating.
- Side effect noted, not a code bug: the live `scratch-and-mail` run above moved whatever window was active at approval time to the scratchpad and opened Outlook, per its own existing (unrelated) behavior; a previously-open Todoist webapp window was separately observed to have closed on its own sometime during this session while another agent shared the same checkout/desktop — not reproduced, not attributed to this change; the user can relaunch it with `open Outlook`/`open my planning` if wanted, no state was lost.
- Cross-session note: another agent/session was actively working (and independently live-testing this same `POST /v1/runs/<id>/feedback` endpoint against the same running service) in this shared checkout during this work — visible as extra `jarvis.service` restarts and one duplicated ADR-020/PROGRESS entry (deduplicated in place, kept the version matching the code actually on disk) and as occasional 409s from a busy lock held by the other session's in-flight request, not a defect in this change. Also `209b13d`/`e94aa4e` committed by that session earlier (see A-004 above); no file overlap with this assignment's changes.

## 2026-09-09 — A-006: log retention + temp cleanup

**Before:** `logs/` (already fully gitignored — nothing was ever tracked) grew unbounded on disk: one file per run under `logs/runs/` and `logs/debug/`, one archive per `VERSION` bump, plus assorted one-off scratch from test/demo scripts and manual `hyprctl`-redirect debugging. The Chromium `logs/overlay-profile/` cache alone reached 150MB+ on this host.

**After:** `brain/journal.py`'s `prune(directory, pattern, keep)` automatically deletes the oldest files beyond a cap — 200 for `logs/runs/*.log` and `logs/debug/*.jsonl`, 20 for `logs/journal/archive/*.jsonl` — checked once per new run or once per version-bump rotation, never on a poll. `logs/feedback/needs-review.jsonl` is deliberately exempt (meant to be read and cleared by a human). Separately, `./scripts/clean-temp-logs.sh` removes known one-off scratch (stale evidence dumps, ad-hoc redirects, `__pycache__`) any time, with `--profile` to also clear the overlay's Chromium cache once a live `hyprctl` check confirms no overlay window is open. See ADR-021 and `docs/LOGGING.md`.

- Audited first: `git ls-files logs/` was already empty and `.gitignore`'s bare `logs/` line already covers everything under it — no `.gitignore` change was needed, nothing to `git rm --cached`.
- `brain/journal.py`: `prune()` + `RUN_LOG_KEEP`/`DEBUG_KEEP`/`ARCHIVE_KEEP`, wired into `Journal.write()`.
- `scripts/clean-temp-logs.sh` (new): removes `demo-evidence.json`, `host-evidence.json`, `doctor-final.txt`, `manual-actions.jsonl`, `clients-after-*.json`, `*.tmp`, `__pycache__`; `--profile` for the overlay cache.
- `docs/LOGGING.md` gained a "Retention and temp cleanup" section; `README.md` got a one-liner.
- Tests: 6 new in `tests/test_journal.py` (`prune` newest/oldest/no-op/under-cap, `Journal.write` pruning run logs only on a `prompt` phase and the archive only on rotation).

### Verification
- `python3 -m unittest discover -s tests` — **70 tests** pass (6 new). `shellcheck`/`doctor.sh --syntax` clean.
- Live on this host: ran `./scripts/clean-temp-logs.sh` for real — removed 5 stray scratch files (`demo-evidence.json`, `host-evidence.json`, `doctor-final.txt`, `manual-actions.jsonl`, `clients-after-skills.json`, the last three of which were leftovers from other concurrent sessions' manual testing, not from any script in this repo) plus 4 `__pycache__` dirs. Then ran `--profile` with the overlay closed — correctly cleared the 154MB `logs/overlay-profile/`; confirmed via `toggle-overlay.py` that the overlay still launches, single-instances, and closes correctly with a freshly recreated profile. The safety check itself was caught and fixed mid-implementation: an initial `pgrep -f 'chromium.*jarvis-overlay'` guard false-positived by matching the verifying shell's own command-line text (which contained that literal string); replaced with the same `hyprctl`-based `is_overlay()` check the rest of the codebase already uses.

## 2026-09-09 — A-010: overlay lifecycle bugs (input wipe, restore-on-reopen, single-instance hardening)

**Before:** typing an answer into the Q&A/report box got wiped almost instantly (every ~700ms, mid-keystroke); closing and reopening the overlay always started from a blank "Ready" screen even though the server still had the last run's full state; the hotkey's "already open somewhere" behavior felt like it might leave a second, unreachable copy; the original prompt wasn't shown next to the A-005 feedback controls.

**After:** `render()` only resets `qaAnswer`'s value/focus and `runBtn`'s focus on an actual state transition (tracked via a cheap signature), not on every 700ms poll of an unchanged question/plan — this was the literal root cause of the "removed instantly" bug. The submit handler clears the input immediately on send instead of leaving stale text in a disabled box. Reopening the overlay now fetches and re-renders the last known run's state instead of starting blank, and resumes polling if it's somehow still in progress. `core.is_overlay()` matches any class containing `jarvis-overlay` (not just the two literal ADR-013 variants), and `toggle-overlay.py` self-heals if it ever finds more than one overlay window. The feedback row now shows the prompt it applies to. See ADR-022.

- `overlay/app.js`: `lastRenderKey` + signature-gated resets in `render()`; `setConsoleTarget` clears the key on a genuine run change; submit handler clears/restores `input.value`; startup IIFE fetches+renders (and resumes polling) the last run instead of only wiring the console button; `renderFeedback` shows `result.prompt`.
- `overlay/index.html`/`style.css`: `#feedback-prompt` element + layout.
- `actions/core.py::is_overlay`: substring match instead of an exact-literal list.
- `scripts/toggle-overlay.py`: self-heal branch for >1 overlay-class window (keep the focused one or the first, close the rest).
- Tests: `tests/test_jarvis.py::test_is_overlay_matches_known_and_unseen_chromium_variants`; `tests/overlay.test.cjs` extended with a repeated-poll-doesn't-wipe-typing regression, an input-clears-on-send assertion, and a second isolated vm-context scenario proving a reopened overlay restores the last run's reply/steps/feedback prompt instead of starting blank.

### A debugging note: an apparent hang that wasn't one
While verifying the input-clear fix, `node tests/overlay.test.cjs` started hanging indefinitely with zero output — no crash, no error, nothing, well past any reasonable timeout. Bisection was made harder by an accidental `git stash`/`git stash pop` mid-session (recovered cleanly, but left `overlay/app.js` briefly in a half-reverted intermediate state that produced confusing, inconsistent bisection results before being noticed and fixed). The eventual root cause, found via inline `console.error` checkpoints: a pre-existing assertion, `assert.equal(...prompt, elements['#prompt'].value)`, read the input's value *after* `handlers.submit(...)` had already run — which used to still hold the typed text, but now (correctly, per this fix) holds `''` once cleared on send. That assertion started throwing, but its rejection was never reported: an *unrelated*, already-latent orphaned background poll chain in the test mock (documented in earlier comments in this same file, from the original A-005/self-improve work — the mock's `setTimeout(fn){fn()}` calls synchronously rather than after a real delay, so a `poll()` call that never reaches a terminal status recurses via real microtask hops without ever winning the race to report the crash) kept the event loop alive indefinitely, starving Node's unhandled-rejection reporting past any timeout used to detect it. Fixed the test to compare against the prompt captured *before* submission and to assert the input is empty afterward, rather than fixing anything in the (correct) product code. No product behavior changed as a result of this detour — it was purely a test correctness fix once the real bug (the outdated assertion) was found.

### Verification
- `python3 -m unittest discover -s tests` — **71 tests** pass (1 new). `node tests/overlay.test.cjs` — both scenarios pass. `shellcheck`/`doctor.sh --syntax` clean.
- Live on this host (service restarted to load the change): `toggle-overlay.py` verified branch-by-branch via `hyprctl` — open when none exists, focus (not close) when it exists but isn't the active window, and — after manually granting it real focus via `dispatch('focuswindow', …)`, since spawning it through this sandboxed session doesn't grant real window focus the way a user's keypress would (the same documented limitation noted in `scripts/verify-host.py`) — correctly closes when it *is* focused. A real `toggle scratchpad` run was submitted, approved, and completed through the live service; `GET /v1/runs/<id>` confirmed `prompt`/`status`/`feedback` are all present and correct for the restore-on-reopen path to consume. A genuine multi-window self-heal scenario could not be reliably reproduced live in this environment for the reason above; that branch is covered by code review and the straightforward nature of the list-filter logic rather than a live repro.

## 2026-09-09 — A-007 slash autocomplete (Codex)
Implemented a single UI registry for report/feature/backlog/dispatch, prefix suggestions,
arrow navigation, Tab/Enter completion and first-Escape dismissal. Completion sends no run;
arguments remain untouched. Existing routes and approvals are unchanged.
Validation: 71 Python tests and overlay tests pass, including completion/no-send/Escape cases.
A-010 restore/input-preservation scenarios remain green. Next authorized assignment: A-008.

## 2026-09-09 — A-008 Training mode (Codex)
Added /train and Training/Back controls, issues/backlog/neutral/eval panels, version and
bounded current-journal metrics, SESSION/QUEUE context, confirmed assignment generation,
NEW_AGENT/CONTINUE handoffs and local slots with busy rejection / queue-until-free intent.
Preview does not write; confirmation is single-use and refuses stale ownership/file state.
No real agent dispatch exists, and copy/status text explicitly says prepared locally.
Evidence: 77 Python tests pass; Training UI mock covers enter/back, preview/cancel/confirm
and duplicate-click prevention. Existing overlay scenarios pass. Live authenticated API
returned 4 assignments and 24 problem records; unauthenticated GET rejected; work preview
listed 3 files and wrote none. Live Doctor passed. Browser connector reported no browser,
so rendered visual QA remains a human validation task. Version 0.5.0 resets the current
journal on the next service restart/write. Next authorized assignment: A-009.

## 2026-09-09 — A-009 human validation (Codex)
Added the JSON feature catalog and generated FEATURES index, guided steps and expected
outcomes, explicit human Verify/Fail previews, version/revision/date/notes/run evidence,
and definition hashes that require retesting changed guides. All seeded features remain
unvalidated; automated checks do not create human evidence. Failed results can open the
existing deterministic intake with the tested feature's context, and still await reviewed
Run before filing. Verify closes no issues. START and assignment authoring rules require
future feature work to update human validation entries.
Validation: 82 Python tests and all four UI smoke scenarios pass; tests cover confirmation,
changed guides, correct failed-run attribution and no automatic filing. Isolated real HTTP
smoke on localhost:17421 returned 9 guides and a two-file result preview with zero writes;
all three new JavaScript routes returned 200. No visual browser surface was available.
Version 0.5.1 archives CURRENT on restart/first write. The shared checkout was switched by
another session during A-009; its named stash 5b29ade was preserved and restored without
loss into ~/Work/omarchy-jarvis-training. The other session's cherry-pick was left alone.
The authorized A-007 → A-008 → A-009 batch is implemented; next is PR integration/checks.

## 2026-09-09 — A-011: open apps by name (Spotify + general .desktop matching)

**Before:** saying "spotify" produced an empty plan and a "not a supported action" reply — `open_webapp` only covers four fixed webapps.

**After:** `open_app_by_name` resolves any text against installed `.desktop` launchers (exact → unambiguous prefix/substring → single closest fuzzy match; a genuine tie lists the candidates instead of guessing) and delegates the actual open-or-focus to Omarchy's own `omarchy-launch-or-focus`, which already handles "focus if a matching window exists, else launch" — no new window-polling logic was needed for that part. See ADR-023.

- `actions/core.py`: `desktop_entries()`, `resolve_app()`, `launch_command_for()` (strips `.desktop` field codes — the whole token, not just the code), `open_by_name()`; new `actions/open_app_by_name` CLI.
- `brain/tools.json`/`system_prompt.md`/`server.py`: new tool wired into `tool_argv`/`action_label`, plan-schema example, and system-prompt disambiguation from `open_webapp`.
- Tests: `tests/test_jarvis.py::OpenByNameTest` (9 cases) using synthetic `.desktop` fixtures and mocked `hyprctl`/`Popen`.

### Verification
- `python3 -m unittest discover -s tests` — **80 tests** pass (9 new). `shellcheck`/`doctor.sh --syntax` clean.
- Live on this host: `./actions/open_app_by_name --name spotify` for real launched Spotify (not previously running) and reported its window correctly (`class: Spotify`, real address); calling it again focused the *same* window instead of launching a duplicate. Also dry-run verified against several other real installed apps (`Spotify`, `Discord`, `Google Photos`) and a no-match case.
- Not verified live end-to-end through the HTTP planner/overlay in this session: this work was done in an isolated `git worktree` on `main` because the shared checkout's working tree was mid-flight with another agent's uncommitted A-007 work on `codex/training-track`, and the live `jarvis.service` (bound to port 7421) runs from that shared checkout — starting a second instance to test against would have conflicted. The action itself, `tool_argv`/`action_label` wiring, and the JSON-plan example are all covered by direct CLI runs and unit tests instead.

### A note on working in parallel with another agent in the same checkout
This repo has no worktree isolation between concurrent sessions by default (noted in earlier passes). For this assignment specifically, `git worktree add` was used to get a clean, isolated `main` checkout for A-011's own commit, rather than risking `git checkout`/`stash` against a shared tree that had another agent's uncommitted, differently-branched work sitting in it. Recommend this as the default pattern whenever two assignments are genuinely running in parallel on this host.

## 2026-09-09 — A-012: open YouTube + a planner honesty guard against empty-action lies

**Before:** "open youtube" produced `{"actions": [], "reply": "Opening YouTube."}` — a false success claim that skipped approval entirely (zero-action plans go straight to `done`) and was rated "bad" by the user (run `fad6f832`, via A-005's own feedback controls).

**After:** `YouTube` is now in `open_webapp`'s `APPS` map — a real webapp, not just a `.desktop`-dependent resolution, so it works even on a host without a local YouTube launcher installed. Separately, and more generally: if the planner ever produces an empty-action plan whose reply *itself* claims an action ("Opening…", "Moving…", "Switching…", etc.), the reply is rewritten to an honest "I don't have a way to do that yet" before it ever reaches the user — in both the default JSON planner and the opt-in tools-loop planner. See ADR-024.

- `actions/core.py`: `YouTube` → `https://www.youtube.com/` in `APPS`.
- `brain/tools.json`: `YouTube` added to `open_webapp`'s enum.
- `brain/server.py`: `FALSE_ACTION_CLAIM_RE` guard in `json_plan()` and `plan_tools_run`; a new `open youtube` → `open_webapp` JSON-plan example.
- `brain/system_prompt.md`: explicit "never claim an action without a matching tool call" instruction, plus YouTube added to the open_webapp list.
- Tests: 5 new (the exact `fad6f832` reply gets rewritten; an honest empty reply is untouched; a real action's "Opening…" reply is untouched; the same guard on the tools-loop path; YouTube present in `APPS`).

### Verification
- `python3 -m unittest discover -s tests` — **85 tests** pass (5 new). `shellcheck`/`doctor.sh --syntax` clean.
- Live on this host: reproduced the *original* bug for real against the live service before this fix landed — "open youtube" (with YouTube not yet in `APPS`) actually returned a plan with a *different* hallucinated target ("Opening Google Calendar.", a real but wrong action) on one attempt, confirming this model is unreliable for unsupported names in more than one way; the journal's own record of run `fad6f832` independently confirms the exact empty-action variant this fix targets. After the fix, `./actions/open_webapp --name YouTube` really opened YouTube (`class: brave-www.youtube.com__-Default`) and a second call correctly focused the same window instead of duplicating it. Did not re-drive the fixed behavior through the live HTTP planner end-to-end this session — the shared checkout's live `jarvis.service` was under real concurrent use (repeated 409s) partway through verification; the server-side honesty guard is deterministic string-matching logic covered directly by unit tests instead, and the `open_webapp`/YouTube half was verified for real via the CLI action.
- This work was done in its own `git worktree` (`~/Work/omarchy-jarvis-a012`, branch `a012-open-youtube`), consistent with the A-013-in-progress pattern, since A-007/A-008/A-009 continue in parallel on `codex/training-track` in another worktree.
## 2026-09-09 — A-013: isolated worktrees by default for parallel agents

Shipped ADR-024 and mandatory concurrent-agent isolation in START, AGENTS, desk README and CONTINUE/PARALLEL/NEW_AGENT prompts. Exact commands cover a unique branch from origin/main, reuse of assigned trees, branch push, and clean/merged/unowned cleanup without force. Serial work remains optional. Chose documented commands rather than a helper. This applies A-011's lesson: uncommitted training-track work in the shared checkout made checkout/stash unsafe; a separate main-based worktree let A-011 ship.

`assignment-status.sh` now lists branches/worktrees and cleanliness with optional git locks disabled, warns about dirty other branches, and explains that QUEUE/SESSION are branch-local snapshots requiring claim reconciliation. It prints no changed filenames or contents and never modifies other trees. Policy retains area/path restrictions, shared-service coordination, and merge reconciliation for common bookkeeping.

Verification: all **80 Python tests** pass; shellcheck across scripts/skills, `doctor.sh --syntax`, JS syntax, both overlay test scenarios, and `git diff --check` pass. Running status on this host identified the dirty A-012 tree and current A-013 changes while the primary/training trees were clean. Live `doctor.sh` could not complete within the sandbox (Ollama/Hyprland/local socket and GitHub connectivity checks failed; report-last-failure lacks a local prior run). No product changes or service restarts. A-013 moved to done; QUEUE/INDEX/SESSION updated. Work stayed in `/home/omarchy/Work/omarchy-jarvis-a013`; delivery branch `a013-parallel-worktrees`. Batch size 1: A-012 and overlay work remain untouched.

### 2026-09-09 — desk: merge A-013 + file A-014 hygiene burn
- Merged `a013-parallel-worktrees` into main (conflict reconcile).
- A-012 already on main; bookkeeping done.
- Queued **A-014** for Codex keep-going hygiene until session tokens.

### 2026-09-09 — A-014 chunk 1: bookkeeping
Claimed by Codex on `a014-hygiene` in the assigned absolute worktree; desk and training SESSION checked read-only, overlay claims untouched. QUEUE/INDEX matched disk; assignment body reconciled. GitHub confirms smoke #8 closed; corrected stale local backlog row and retained fixture with triage note. Assignment-status and syntax Doctor pass; baseline 85 Python tests pass. No live service restart. Next: test gaps.

## 2026-09-10 — A-014 Chunk 2
- Worked: baseline 85 tests green; added app-plan approval and YouTube missing-window regressions (87 tests). Python, doctor syntax, ShellCheck and overlay checks pass. No live desktop actions or service changes.

## 2026-09-10 — A-014 Chunk 3
- Worked: removed unreachable duplicate/recipe-combination checks after the JSON planner’s existing one-action limit, plus three unused test imports. Existing multi-action rejection test and all 87 tests pass. Kept callable action/script entry points; no speculative deletions.

## 2026-09-10 — A-014 Chunk 4
- Worked: shared empty-plan guard catches blank replies, bare completion and common first-person claims; tools completion now uses executed labels. 89 tests pass; VERSION 0.4.2. Limitation: lexical guard is not semantic verification. Shared live service was not restarted (other track owns it); deploy/restart and CURRENT version rotation remain for merge handoff.

## 2026-09-10 — A-014 Chunk 5
- Worked: malformed CURRENT headers now archive byte-for-byte instead of blocking all later evidence; removed redundant plan cleaning before Journal.write. 91 tests pass, including quiet access logging and damaged-header recovery; existing debug/retention/version-rotation tests stay green. No live journal reset.

## 2026-09-10 — A-014 Chunk 6
- Worked: clarified batch override, default approval behavior, planned overlay features vs shipped code, partial validation catalog, lexical honesty limits, and file-count retention vs unbounded CURRENT bytes. Human validation remains unvalidated; no overlay assignment bodies or UI changed. Checked edited docs against implementation and git diff whitespace.

## 2026-09-10 — A-014 Chunk 7 / handoff
- Worked: experimental tools executor stops before unreviewed follow-up actions; both planners enforce intake-only issue filing. Removed the now-unreachable six-turn loop. All 93 Python tests, doctor syntax, ShellCheck, JS syntax and overlay behavior checks pass.
- Failed/limited: sandboxed host doctor could not access sockets; rerunning with host access passed all checks except report-last-failure --dry-run. In a fresh checkout without logs/runs, that skill’s find pipeline exits under set -e/pipefail before its intended no-log dry-run fallback. skills/ is outside A-014’s allowed paths; follow-up owner should fix and test it with no log directory. No issues filed, desktop mutations, service restarts or changes to other worktrees.
- Handoff: chunks 1–7 complete on a014-hygiene, VERSION 0.4.2; merge owner must reconcile shared bookkeeping with the overlay track, deploy/restart the shared service, and verify the first-write CURRENT rotation. No live deployment claimed.
### Training batch integration and final checks
Merged latest main into the isolated training branch, preserving A-011 and queued A-012/A-013.
Resolved documentation conflicts and kept ADR-023 for A-011; Training-track decisions are
ADR-024/025/026. Added A-011's app-by-name guide to the machine-readable catalog (10 entries).
Validated slot identifiers and registry shape before they can contribute to handoff paths.
Final evidence: 92 Python tests, all four UI smoke scenarios, all JS syntax checks, ShellCheck,
Doctor syntax and live Doctor pass. The isolated Doctor initially failed because logs/runs/
had not been initialized by service startup; creating that empty runtime directory made its
existing no-history dry-run path pass. Final isolated HTTP smoke returns 10 guides, all JS
routes, and an unconfirmed two-file validation preview with zero writes. Human visual
validation remains pending because the browser connector exposes no browser on this host.

### 2026-09-10 — desk: merge a014-hygiene + codex/training-track into main
- Resolved ADR numbering (YouTube/honesty 024, worktrees 025, slash 026, training 027, validation 028).
- VERSION → 0.5.2; QUEUE empty; A-001…A-014 done.
- Restart jarvis.service still required for live overlay/training.

### 2026-09-10 — A-015: plan/step detail for skill recipes
- Alex validated feat-overlay-chat on 0.5.2 in Training mode and noted a `run_skill` plan
  (e.g. "open my planning in a new workspace") only ever showed the bare skill slug, not
  what it would actually do or the parameters involved — poorly readable for a human.
  Training generated A-015 from that note; scoped to `skills/` only at first, then
  expanded to include `brain/server.py` + `brain/system_prompt.md` with Alex's explicit
  sign-off after tracing the terse text to `action_label()`/`json_plan()`'s reply, since
  no `skills/`-only change could have altered what's actually displayed.
- Worked: `action_label()` now appends the skill's own `SKILL.md` description for
  `run_skill` actions (step list + final "Completed: …" message); `json_plan()`
  deterministically swaps a run_skill action's model-written reply for that same
  description, so the pre-approval preview headline names what will run instead of
  trusting the 3B model's terse guess; a new `summarize_step_result()` turns a finished
  `run_skill` step's raw JSON stdout into a plain sentence ("Created workspace 3; opened
  Todoist; opened Google Calendar.") instead of a truncated JSON blob, with a safe
  fallback to raw (truncated) stdout for every other tool or an unrecognized shape.
  overlay/, actions/ and every other tool's label/reply path are untouched.
- Bumped VERSION 0.5.2 → 0.5.3; feat-overlay-chat's `jarvis_version_shipped` bumped to
  match and given a fifth guided step exercising a skill-based plan preview, which
  (correctly, via `definition_hash`) flips it back to unvalidated for Alex to re-test.
- Evidence: 109 Python tests pass (82 in test_jarvis.py, including 5 new ones for
  `skill_description`/`action_label`/`summarize_step_result`; two pre-existing tests
  updated to expect the richer text). `doctor.sh --syntax` and both affected skills'
  `--dry-run` pass. Fixed as a side effect: `test_schema_seed_and_missing_attestation`
  was failing before this change (the earlier training-authored bookkeeping commit had
  left feat-overlay-chat "validated" in the real catalog.json, which the test copies
  into its fixture and asserts is all-unvalidated) — invalidating feat-overlay-chat here
  restored that invariant without touching the test's fixture-seeding design.
- Limitation: no live Ollama/Hyprland/overlay in this sandbox, so the deterministic
  server-side paths were unit-tested but the actual overlay rendering and a real model's
  `reply` text for non-run_skill tools were not exercised end-to-end. Shared jarvis.service
  was not restarted (forbidden for this session); Alex should restart from main and
  re-run the feat-overlay-chat guide (step 5) on 0.5.3.

## 2026-09-10 — desk: queue A-016 Training window overhaul
- Alex: Training must be a main self-improve surface; current UI too chaotic.
- Wanted: separate Hyprland window, top stats bar, feature nav buttons, Problems-first (color-coded list, dismiss/check-off, detail+edit+save, priority, generate assignment).
- Filed [A-016](assignments/active/A-016-training-window-overhaul.md); kept earlier plan-detail ask as A-015 (lower priority, same area).

## 2026-09-10 — desk: queue A-017 Training Assignments panel
- After Problems: queue list + click/detail/save; generate assignment from selected problem (local model or on-machine agent); handoff button → Agent monitor.
- Filed [A-017](assignments/active/A-017-training-assignments-panel.md); QUEUE order A-016 → A-017 → A-015.

## 2026-09-10 — desk: queue A-018 Training Agent monitor
- Agent tiles; click → overview + open visible Hyprland agent window (not hidden background).
- Left assignment list to spin up/assign; preselect from A-017 handoff; interactive parallel-aware queue board.
- Filed [A-018](assignments/active/A-018-training-agent-monitor.md); order A-016 → A-017 → A-018 → A-015.

## 2026-09-10 — A-016 Training window and Problems triage
- Completed one assignment in isolated a016-training-window. Read all other SESSION/QUEUE snapshots: handoffs completed; A-015's queued row on main was stale, its implementation awaits merge.
- Added separate Training app/profile/class and fixed authenticated launcher, scannable metrics and three navigation panels. Problems retain original bounded/redacted context, saved fields, P0–P3 priority and local status; confirmed local deletes keep tombstones. Saved-problem assignment previews include edits, priority and original evidence with stale-record rejection.
- Passed 112 Python tests, all UI smoke scenarios, all JS syntax, ShellCheck, Doctor syntax, and isolated HTTP assets/authenticated save/assignment confirm/delete using disposable data on port 17421. Fixed test fixture dependence on real human-validation history without changing Alex's evidence.
- Host Doctor passes except the previously documented missing-logs/runs report-last-failure dry-run defect (skills outside scope). Hyprland clients/workspaces read successfully; no Jarvis windows were open. Browser connector provides no browser, so visual QA and real window launch remain unvalidated in feat-train. No shared-service restart during isolated work.
- VERSION 0.5.4, ADR-030, README and human guide updated. A-017 then A-018 are next; no second assignment claimed. Alex requested merge/cleanup of all finished branches after this assignment.

### A-015/A-016 integration — 2026-09-10
- Integrated a015-plan-detail into a016-training-window with ordinary merge ancestry. Product code and validation catalog merged automatically; reconciled VERSION to 0.5.4, retained ADR-029/030 and both progress records, archived A-015, and preserved queued A-017/A-018.
- Combined verification: 116 Python tests and all UI smoke scenarios pass. Existing A-013, A-014 and training-track commits are already ancestors of main. Final branch cleanup will preserve ignored runtime data in a local archive before removing clean, finished trees.
- Shared-service restart requires coordination under the worktree instructions; asked Alex after preparing and testing the concrete merged result.

### Final branch cleanup — 2026-09-10
- Pushed integrated main at 11d4037. All five non-main branches are merged: a013-parallel-worktrees, a014-hygiene, codex/training-track, a015-plan-detail, a016-training-window. Removed their clean finished worktrees without force, deleted local branches with branch -d, and deleted corresponding remote branches after the main push succeeded.
- Preserved ignored runtime directories before removal in `/home/omarchy/Work/omarchy-jarvis-worktree-archives-20260910/` (one restricted-permission tar.gz per removed tree). Canonical runtime data was not changed. Stopped the isolated temporary HTTP test server.
- Remaining checkout/branch: `/home/omarchy/Work/omarchy-jarvis` on main. Batch 1 complete. A-017 is next, then A-018. Shared-service restart awaits Alex's coordination response; no live deployment or human validation claimed.

## 2026-09-10 — A-017 Training Assignments panel
- Picked up mid-flight from Codex (`a017-assignments-panel`, claimed `in_progress`, uncommitted): the feature implementation, tests and docs were already functionally complete, but the session ran out of tokens before the closing steps — checklist/status/QUEUE/INDEX/PROGRESS were still stale and nothing had been committed. Reviewed the full diff (brain/training.py, brain/server.py, overlay/training.html+.js+.css, new overlay/assignments.js, tests) before finishing it, rather than trusting the in-progress marker alone.
- Assignments is now a real queue/detail/save surface, not a title dump: click a row for the full brief (title/area/priority/goal/checklist/notes/allowed+forbidden paths); queued/blocked, unclaimed briefs are editable, owned or closed ones are read-only; **Preview Save / Add** shows exact brief/QUEUE/INDEX/SESSION-note diffs and a revision hash rejects a save over intervening changes. New drafts can link a saved Problem (inheriting title/notes/area/priority/evidence) or start blank. **Generate draft** offers a local-Ollama mode (schema-constrained JSON, explicit preflight rejecting any remote/cloud model, writes nothing) or an on-machine-agent mode (copy a prompt, paste back its JSON — Jarvis never launches or contacts the agent itself). **Hand off to agent** jumps to a now-separate Agent monitor nav panel with the saved assignment preselected.
- Evidence: 127 Python tests pass (up from 116 at A-016; new `tests/test_assignments.py`), all four `tests/*.cjs` JS suites pass including the new `assignments.test.cjs`, `doctor.sh --syntax` passes. VERSION 0.5.4 → 0.5.5; ADR-031 records the design; README and `feat-training-assignments` validation guide (8 guided steps) added, left unvalidated for Alex.
- Limitation: no live Ollama/Hyprland/browser in this sandbox — the local-generation and on-machine-agent paths, and the Agent-monitor handoff deep-link, are unit/HTTP-tested but not exercised against a real model or window manager. No shared-service restart performed.
- Merged `a017-assignments-panel` into `main` and pushed; removed the finished worktree/branch after confirming a clean, merged status. Continuing to A-018 (Training Agent monitor) per Alex's explicit "move on to the next assignment."

## 2026-09-10 — A-018 Training Agent monitor
- Alex: see and steer local coding agents without them living in the background — slot metadata alone was explicitly rejected as the main UX; wanted the same window he'd get launching and pasting a prompt into a terminal himself.
- Agent monitor is now a tile grid (kind/idle-busy/current assignment per slot) with a click-through detail overview (status, current/queued assignments, last handoff, and for non-human slots an **Open agent window** button) plus a read-only queue board naming each assignment's current worker straight from disk QUEUE/SESSION. New `scripts/open-agent.py` (mirrors `scripts/open-training.py`) opens/focuses a real per-slot terminal via `omarchy-launch-or-focus-tui --app-id=jarvis-agent-<slot-id> <claude|codex>` — never a hidden process; a second click focuses instead of relaunching. New `POST /v1/training/agent-window` resolves the slot's kind server-side (`training.find_slot`) rather than trusting the request body. Confirming a "prepare now" handoff auto-opens the resulting window. The existing idle/busy toggle and A-017 handoff deep-link (preselecting an assignment from Assignments) both carried over onto the new tile UI.
- Evidence: 138 Python tests pass (up from 127 at A-017; new `tests/test_agents.py` covering the script's launch/focus/reject paths and the HTTP route's server-side kind resolution), all five `tests/*.cjs` JS suites pass including new `tests/agents.test.cjs`, `doctor.sh --syntax` passes. VERSION 0.5.5 → 0.5.6; ADR-032 records the design; HOST.md documents the window-class/app-id convention and installed CLI mapping; README and `feat-agent-monitor` validation guide (7 guided steps) added, left unvalidated for Alex.
- Limitation: no live Hyprland/terminal in this sandbox — the launch-or-focus path is unit-tested (mocked `hypr`/`dispatch`/`Popen`) but not verified against a real window; Alex should click Open agent window for real once merged and check `logs/agent-windows/<slot-id>.log` if a window doesn't appear. No auto-typed/pasted prompt into the launched terminal — Copy handoff remains the paste step. No shared-service restart performed.
- This closes the A-016→A-017→A-018 Training track. Merging into `main`, pushing, and removing the finished worktree/branch next.

## 2026-09-10 — desk: queue A-019 proposed-action bubble UX
- Alex: plan info still lands as hard-to-read text below the proposed bubble; wants it inside the bubble, intuitive, wrap only if needed.
- Follow-up to A-015 (brain labels). Filed [A-019](assignments/active/A-019-proposed-action-bubble-ux.md).

## 2026-09-10 — desk: queue A-020 Validate features UX
- Verify/Fail not removing items / results not obviously recorded; include-validated should show reports.
- Run id requested but never shown by Jarvis.
- Automate mechanical guided steps; Alex judges desktop outcome after Run.
- Filed [A-020](assignments/active/A-020-validate-features-ux.md); queued ahead of A-019.

## 2026-09-10 — A-020 Validate features UX
- Audited `training.preview`/`confirm` against `tests/test_validation.py`: the write path
  already persisted correctly end to end (existing `test_result_requires_confirm_and_records_version`
  proves it). The real bug was UX: a confirmed guide stayed open with the same checked boxes,
  so a real write looked like nothing had happened.
- Fixes: (1) `validationSaved()` closes the guide back to the list on a confirmed result;
  the list itself now prints each item's last report (result/date/version/notes) inline,
  visible without a click — addresses "not only re-run empty forms." (2) The chat overlay's
  footer now shows the current run's id (click to copy) — it was already used internally for
  console/feedback but never shown to a human; the guide's run-id field is relabeled to make
  "leave it blank" explicit. (3) A guided step can now be `{"text","kind":"auto","prompt"}`
  in addition to a plain string — an auto step gets a **Run this step** button that submits
  its literal `prompt` through the same `/v1/run` a chat send uses, polls the same way the
  overlay's own poll loop does, shows the observed reply/status inline, and captures the run
  id automatically. It never approves/denies anything — a plan reaching `awaiting_approval`
  is left exactly there for Alex to decide in chat; the step's checkbox is still a human tick.
  `feat-overlay-chat`'s three "Type: ..." steps are migrated as the reference case; other
  guides' mechanical steps are Training-window UI navigation, not a chat prompt, so they have
  no `auto` candidate under this mechanism yet and stay manual.
- Evidence: 141 Python tests pass (up from 138 at A-018; 3 new in `test_validation.py` for
  the auto-step schema and mixed-shape `report_evidence`), all five JS suites pass (extended
  `validation.test.cjs` for the auto-run/list-report/guide-collapse behavior, `overlay.test.cjs`
  for the visible run id), `doctor.sh --syntax` passes. VERSION 0.5.6 → 0.5.7; ADR-033 records
  the design; `feat-overlay-chat` and `feat-validate` both got updated guided steps (and
  `jarvis_version_shipped` bumps), correctly re-flipping to unvalidated for a fresh pass.
- Limitation: no live Ollama/Hyprland in this sandbox — the auto-step round trip against
  `/v1/run` is unit/mocked, not exercised against a real model. Alex should click **Run this
  step** for real on `feat-overlay-chat` once merged, and confirm the run id shows up both in
  chat's footer and the guide's evidence field.
- A-019 (Proposed-action bubble UX) is next in the same overlay area (serial).

## 2026-09-10 — desk: queue A-021 empty Enter skips report Q&A
- Alex: Enter on empty “how did that go” report should Skip for fast dismiss.
- Filed [A-021](assignments/active/A-021-empty-enter-skips-report-qa.md) (`parallel-ok: YES`).

## 2026-09-10 — A-021 empty Enter skips report Q&A
- Reproduced: `answer()` early-returns on falsy text, so Enter on an empty report-intake answer silently did nothing (not "submits blank" as suspected, just a dead keypress) — Alex had to click Skip or type the word.
- Fix: `#qa-form` submit now sends `'skip'` when the trimmed answer is empty, reusing the existing `answer()`/Skip path; a non-empty answer still sends verbatim. The emoji-only feedback row (`#fb-good`/`#fb-neutral`/`#fb-bad`) is a separate `<section>` outside any form, so Enter there was never a blank-run footgun and needed no change.
- Evidence: new `tests/overlay.test.cjs` case posts an empty Enter and asserts the `/answer` request body is `{text:'skip'}`; all six existing `tests/*.cjs` suites still pass. `scripts/doctor.sh` shows the same single pre-existing failure (`report-last-failure` example skill) on unmodified `origin/main`, confirming it's unrelated.
- Done in isolated worktree `~/Work/omarchy-jarvis-a021-empty-enter-skips-report-qa` (branch `a021-empty-enter-skips-report-qa`), parallel to in-progress A-020 (disjoint files: `overlay/app.js` vs `overlay/validation.js`).

## 2026-09-10 — desk: queue A-023 simplify assignment path scope
- Alex: hard Allowed/Forbidden paths cause constant expansion asks; worktrees already isolate.
- Prefer area + worktree; paths as optional soft hints. Filed [A-023](assignments/active/A-023-simplify-assignment-path-scope.md).

## 2026-09-10 — A-023 simplify assignment scope: area + worktree, not hard path fences
- Real motivating bug found while auditing: `docs/assignments/prompts/NEW_AGENT.txt`'s claim rule said "disjoint area/**paths**," and `scripts/assignment-status.sh`'s claim hint only ever filtered candidates on `queued` + `parallel-ok: YES` — it never actually checked area disjointness against the in-progress row. That combination is exactly what let this session claim A-021 (`area:overlay`) in parallel with A-020 (`area:overlay`, in_progress) earlier today, reasoning their path lists didn't overlap; both landed good changes in separate worktrees, but merging them back into the canonical checkout produced real conflicts across `docs/PROGRESS.md`/`docs/SESSION.md`/`docs/assignments/{QUEUE,INDEX}.md` that a second session had to stop mid-merge to sort out.
- Fix: parallel-safety is now **area disjointness + separate worktree**, full stop — `Allowed paths:`/`Forbidden paths:` become optional soft hints for context, never a claim gate. Updated `START.md`'s Parallel work section, `docs/assignments/{README,TEMPLATE}.md`, and all three paste prompts (`NEW_AGENT`/`CONTINUE`/`PARALLEL.txt`) to state the one unambiguous check: does this row's `area:` differ from every `in_progress` row's `area:`? `scripts/assignment-status.sh`'s claim-hint branch now actually computes that (extracting each `in_progress` row's area column and excluding queued candidates that match), instead of only checking `parallel-ok: YES` — verified against a synthetic same-area in-progress/queued QUEUE.md that reproduces the exact A-020/A-021 scenario and confirms the fixed script now correctly reports "No assignment in queue is possible right now" instead of offering the conflicting row.
- Training's Assignments editor (`overlay/training.html`, `brain/training.py::assignment_fields`) dropped the HTML `required` attribute and non-empty validation on `allowed_paths`/`forbidden_paths`, relabeling them "(optional hint, not a gate)" — field names/labels otherwise unchanged so existing/desk-generated briefs keep parsing correctly.
- Evidence: 142 Python tests pass (up from 141 at A-020; 1 new — blank `allowed_paths`/`forbidden_paths` now save successfully), all six `tests/*.cjs` JS suites pass, `doctor.sh --syntax` passes. ADR-034 records the decision and cites the A-021 merge-conflict evidence directly.
- Out of scope per the brief: no worktree-creation mechanics changed, no other product code (overlay/brain/actions) touched beyond the two minimal string/validation changes the brief explicitly carved out, and historical `done/` assignments keep their old "(required if parallel-ok YES)" wording untouched.
- Done in isolated worktree `~/Work/omarchy-jarvis-a023-simplify-assignment-path-scope` (branch `a023-simplify-assignment-path-scope`), claimed off `origin/main` after the canonical `~/Work/omarchy-jarvis` checkout was found mid an unrelated, unfinished `git merge` of the A-021 branch by a separate session (left untouched, per this repo's never-touch-another-agent's-tree rule).

## 2026-09-10 — A-019 Proposed-action bubble UX
- Alex (follow-up to A-015): brain-side labels improved, but the overlay still showed a bare
  tool/skill name plus `key=value` soup in the actions list, with the actually-descriptive
  reply text stuck in a separate, truncated, below-bubble status line.
- `renderPlan()` now builds each proposed action as a `.action-card`: a friendly title from
  `actionTitle()` (covers all 12 tools in `tools.json`), any leftover argument as a small
  individually-truncating chip (`title=` attribute for the full value on hover), and — for
  `run_skill` — the plan's own `reply` (A-015's skill description) as the card's description
  line. `#status` during `awaiting_approval` now says a fixed "Review the plan below."
  instead of repeating that reply, retiring the redundant text dump Alex named directly.
- Found while testing: `tests/overlay.test.cjs`'s DOM mock never actually cleared `.children`
  on `innerHTML=''` (every other test file's mock does), and the mocked `setTimeout` fires
  synchronously — a background poll chain that outlives a thrown assertion (previously masked
  because the assertion never failed) became a genuine unbounded-growth hang once bubbles were
  multi-node. Fixed the mock and hardened the test's outer `.catch` to `process.exit(1)` so a
  real future failure reports loudly instead of hanging.
- Evidence: 141 Python tests pass (unchanged — overlay-only), all five JS suites pass
  (`tests/overlay.test.cjs` gained bubble-content assertions for both a `run_skill` plan and a
  `report_bug` draft's chips), `doctor.sh --syntax` passes. VERSION 0.5.7 → 0.5.8; ADR-035;
  `feat-overlay-chat`'s guided steps updated to describe the bubble instead of the old
  below-bubble text, correctly re-flipping it to unvalidated.
- Limitation: no live overlay/Hyprland in this sandbox — visual layout (wrapping, chip
  truncation) is CSS-reviewed, not screenshot-verified. Alex should glance at a real plan
  (e.g. "open my planning in a new workspace") once merged and confirm it reads cleanly.
- Live step list (`renderSteps`) untouched — it already shows A-015's server-computed
  `action_label()` text, which was the right fix for that surface already.

## 2026-09-10 — desk: Bitwarden #16 → A-024 + A-025
- Ambiguous multi-match open failed at execute; Alex wants top match + later “other one” with preference weights.
- Split: [A-024](assignments/active/A-024-open-ambiguous-app-top-match.md) actions top-match; [A-025](assignments/active/A-025-app-open-preferences-and-correction.md) preferences/correction.
- Backlog bug moved to `bugs/converted/`; GH #16 left open until both done.

## 2026-09-10 — A-024 ambiguous open_app_by_name → top match
- `resolve_app()` raised "Multiple installed apps match…" whenever a tier (exact/prefix/
  substring) had more than one candidate — e.g. two `.desktop` stems both named "Bitwarden"
  (native + Flatpak) — so `open bitwarden` planned fine but failed at execute.
- Fix: each tier is still checked in the same exact > prefix > substring > fuzzy priority
  order, but a tier with multiple candidates now opens its first (top) entry instead of
  raising — deterministic because `desktop_entries()` already orders most-local-directory
  first, then alphabetically. `open_by_name()`'s result already names the chosen app
  (`entry['name']`), so the reply stays honest about which one launched with no extra change.
  A-025 can build preference weights / "the other one" correction on top of this later.
- Evidence: 143 Python tests pass (2 new: substring-tier tie-break, and a duplicate-Name
  fixture matching the actual #16 shape); `doctor.sh --syntax` passes.
- Out of scope here (left for A-025): learning/preference store, correction utterances,
  closing the wrong window after a correction.

## 2026-09-10 — A-022 fix open cliamp plan/tooling (issue #15)
- Reproduced from #15's captured log: prompt "open cliamp" got `{"actions": [], "reply": "I
  couldn't find 'cliamp' as an available app..."}` — an honest empty plan (not a false-success
  claim), but wrong: the model declined instead of calling `open_app_by_name`, which does its
  own installed-app lookup (exact/prefix/substring/fuzzy, A-024) and would have either found
  it or reported "not installed" honestly. `brain/system_prompt.md` told the model to call
  `open_app_by_name` for "any other installed app by name" but never said what to do about a
  name it doesn't personally recognize — for an unfamiliar or obscure app, the 3B model
  apparently defaults to declining rather than trying.
- Fix: `system_prompt.md` now explicitly says to call `open_app_by_name` even for a name you
  don't recognize, and never to decline/apologize on that basis alone — the tool's own result
  is the source of truth on whether it's installed. Brain-only change (no actions/ or overlay/
  touched), per the assignment's scope.
- Evidence: 144 Python tests pass (1 new, guarding the instruction text itself since the
  actual model behavior can't be exercised without a live Ollama in this sandbox);
  `python3 -m compileall` clean.
- Limitation: this is a prompt-engineering nudge, not a guarantee — matches ADR-024's own
  precedent that a small model's reliability gap can be reduced, not eliminated, by a clearer
  instruction. Alex should retry "open cliamp" for real once this restarts and confirm it now
  either opens CLI Amp or gives an honest "not installed" instead of an apology.

## 2026-09-10 — A-025 app-open preferences + “the other one” correction (#16)
- After A-024, `open bitwarden` launched the top match but there was no way to say the other
  one was meant, close the wrong window, or remember that choice.
- Fix: `~/.config/jarvis/app-preferences.json` (XDG, not repo-tracked) stores per-query stem
  weights and a 15-minute `last_open`. `ranked_apps()` applies weights inside A-024's existing
  exact > prefix > substring > fuzzy tiers. Phrases like “no, the other bitwarden” /
  “the other one” / “not that one” are intercepted before intake and the JSON planner and
  become one reviewed `correct_app_open` action: close the recorded address only if that
  window still matches the opened entry, launch the next-ranked stem, bump its weight.
  No recent open (or a named mismatch) is honest empty-plan chitchat, not a doomed Run.
  See ADR-036.
- Evidence: 153 Python tests pass (9 new: rank-by-weight, next-stem preview, stale/solo
  rejection, close+open+bump, dry-run non-mutation, skip-close when gone, phrase detection,
  planner exclusion, awaiting-approval vs empty plan); all six `tests/*.cjs` suites pass;
  `doctor.sh --syntax` passes. VERSION 0.5.8 → 0.5.9; `feat-open-by-name` guide extended
  and left unvalidated.
- Limitation: no live two-Bitwarden Hyprland round-trip in this sandbox. Alex should
  `./scripts/restart.sh` and run feat-open-by-name's new correction steps on 0.5.9.
- GH #16 closed (A-024 + A-025). Queue empty.

## 2026-09-10 — desk: Wave 0 self-improve foundations
- Decisions in docs/SELF_IMPROVE_ROADMAP.md (ChatGPT reply not pasted into room).
- Queued A-026…A-029; seeded feat-self-improve-* backlog features.

## 2026-09-10 — desk: align Wave 0 to ChatGPT pasted answers
- Runtime/Desk/Forge/Control Plane; ledger wraps QUEUE; unattended PRs after protected main; journal tiers; snapshots if system-affecting only.
- QUEUE order A-027, A-026, A-028, A-030, A-031, A-029.

## 2026-09-10 — desk: queue A-032 ChatGPT plan-vs-codebase review
- Alex: Sol 5.6 ultra-high depth to perfect the self-improve plan against the real tree before Wave 0 implementation.
- Filed [A-032](assignments/active/A-032-chatgpt-plan-codebase-review.md) at head of QUEUE; Wave 0 waits.

## 2026-09-10 — desk: A-032 briefing for Sol without ChatGPT chat
- Added docs/audits/chatgpt-self-improve-discussion-brief-2026-09-10.md (8 answers + sequence + north star).
- A-032: batch 1 only; CONTINUE should name A-032 explicitly.

## 2026-09-10 — desk: Wave 1 latency profiler (A-033–A-035)
- Split ChatGPT text-latency brief; standing work (A-032 + Wave 0) stays first.

## 2026-09-10 — desk: A-036/A-037 Training agent handling usability
- Depth selector/display; rewrite delivery options + immediate prompt path; clarify busy preview; show in-progress work (e.g. A-032).
- Formal stages (shift-up, assign stage, blocked-by-stage/parallel) in editor + agent monitor.

## 2026-09-10 — desk: reshape A-037 away from stage integers
- Prefer gates + blocked-by + QUEUE order over stage 0/1/2 + global shift-up; align with A-026 ledger.

## 2026-09-10 — A-032 codebase-grounded self-improve plan review
- Reviewed the roadmap against approval/execution, Training writes, journals, human validation,
  app preferences, trusted skills, CI, deployment scripts and assignment policy. Kept the
  Runtime/Desk/Forge/Control Plane model and documented where those boundaries are conceptual.
- Live GitHub reads found the private repository cannot enable rulesets or classic branch
  protection on its current plan (HTTP 403). A-027 is blocked until Alex chooses a supported
  plan, deliberate public visibility, or another enforceable host; unattended Forge stays off.
- Separated deterministic CI, runtime anomaly journals, human validation and candidate evals.
  Added A-038 for exact model/prompt/tool/revision identity and durable private evidence before
  A-026/A-028; narrowed and dependency-blocked A-026…A-031. Reconciled and preserved the
  concurrently landed A-033…A-037 assignments; A-036 remains next in QUEUE.
- Evidence: 153 Python tests, five JavaScript suites, shellcheck and `doctor.sh --syntax` pass;
  assignment status and `git diff --check` pass. Docs/planning only; VERSION unchanged and no
  shared service restart required.

## 2026-09-10 — desk: A-039 cross-worktree claim visibility (P0)
- Bug: claim+worktree updates QUEUE only on agent branch; main/next CONTINUE re-claims. Evidence: A-036 in_progress on worktree, queued on main.
- Filed A-039 highest priority, parallel-ok with A-036; desk marked A-036 in_progress on main.

## 2026-09-10 — desk: require merge to main at batch end
- Alex: agents forget to merge; causes conflicts and wasted tokens.
- CONTINUE / NEW_AGENT / PARALLEL / START / prompts README: land on main before stop; report BLOCKED ON MERGE if needed.

## 2026-09-10 — desk: after merge, delete worktree and return to main
- Alex: agents should clean up worktrees and sit on main before the next prompt.
- CONTINUE / NEW_AGENT / PARALLEL / START / prompts README updated.

## 2026-09-10 — desk: queue A-040 test suite optimization
- Alex: too many tests; token waste concern. Snapshot ~153 Python tests; test_jarvis.py largest.
- Goal: smoke vs full, cull redundancy, teach agents not to paste full logs.

## 2026-09-10 — A-039 cross-worktree claim visibility (ADR-038)
- Claimed A-039 itself by pushing its QUEUE/INDEX/SESSION status flip straight to `origin/main`
  before opening a worktree — the first real use of the protocol it implements.
- `scripts/assignment-status.sh`: reads `origin/main`'s `QUEUE.md` as canonical claim truth
  (fetches first; falls back to the local branch with an explicit OFFLINE warning), lists every
  worktree's `SESSION.md` Active goal, and cross-checks each worktree's local `QUEUE.md` against
  canonical rows, printing `MISMATCH` for any unpushed/stale claim (fixed an off-by-one field
  index in the new `row_status` helper found while smoke-testing this).
- `START.md`, `docs/assignments/README.md`, `prompts/{NEW_AGENT,CONTINUE,PARALLEL,README}.md`:
  claim-on-origin/main-first is now step 1 of claiming, ahead of `git worktree add`; added a
  "Recovering a stale claim" procedure to `START.md`.
- Evidence: `./scripts/doctor.sh --syntax` passes; reproduced the original A-036 bug shape
  (uncommitted status edit in one worktree's local `QUEUE.md`) and confirmed
  `assignment-status.sh` reports the `MISMATCH`, then reverted the test edit. Docs/scripts only;
  no shared service restart required.
