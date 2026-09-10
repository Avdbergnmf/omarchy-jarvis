# A-037 — Formal assignment stages (waves) + blocked visibility

- **Status:** queued
- **Area:** area:docs (+ `area:overlay` Training + light `area:brain` training APIs)
- **parallel-ok:** NO (touches assignment schema + Training + QUEUE conventions; after A-036 preferred so monitor can show stage)
- **Wave / stage:** **0** (same usability gate band as A-036)
- **Soft path hints:** assignment TEMPLATE/README/QUEUE/INDEX, `overlay/assignments.js`, `overlay/agents.js`, `brain/training.py`, START.md
- **Blocks / blocked-by:** Best after **A-036**; can follow A-032
- **Links:** Alex 2026-09-10 — waves should be first-class; show blocked-by-parallel and blocked-by-stage

## Goal
Replace informal “Wave 0 / Wave 1” prose with a **formal stage system**:

1. Stages are integers; **lowest is always 0**. Adding a stage can **shift existing stages up by 1** (desk/Training action with confirm).
2. Every assignment has a **`stage:`** (default 0) settable from: Training assignment editor, generation questions, or repo markdown.
3. **Current stage** = minimum stage that still has unfinished work (or explicit “active stage” pointer — pick one, document in ADR).
4. Agent monitor + assignment list show **stage**, and whether an item is **blocked** because:
   - `blocked-by` / dependency on another assignment, or
   - `parallel-ok: NO` collision / area conflict, or
   - **stage &gt; current stage** (not yet released)
5. QUEUE.md remains human-readable but gains a clear stage convention (table column and/or section headers). `assignment-status.sh` should surface stage + blocked reasons.

Done when Alex can see “we’re on stage 0; A-032 in progress; A-033 is stage 1 / blocked” without reading chat history.

## Checklist
- [ ] Schema: `stage` on assignments; migrate existing Wave notes (0 = self-improve foundations usability+control, map A-032/A-036/A-037 → stage 0, Wave 0 foundations → stage 1?, latency A-033+ → higher — **propose mapping in ADR, Alex can tweak**)
- [ ] Desk op: insert stage (shift up) with confirm; edit stage on assignment
- [ ] Training editor + generate flow ask/set stage
- [ ] Agent monitor / board: stage badge + blocked reasons
- [ ] START + assignment README + status script; tests; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Auto-starting next stage agents; changing ledger IMP ids; latency profiler UI.

## Notes
Suggested initial mapping (adjust in ADR if cleaner):  
- **stage 0:** A-032 plan review + A-036/A-037 Training dispatch usability  
- **stage 1:** former Wave 0 (A-026…A-031, A-029)  
- **stage 2:** former Wave 1 latency (A-033…A-035)  
Keep “wave” as optional alias in docs = stage.
