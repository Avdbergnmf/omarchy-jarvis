# Session — A-018

## Active goal
- Assignment: **A-018 — Training Agent monitor** (in_progress)
- Owner: claude-code (this session)
- Branch: `a018-agent-monitor`
- Batch: 2 — A-017 (done, merged) then A-018, per Alex's "move on to the next assignment"

## Checklist
- [x] A-017 done, merged into main (d18da1c), branch/worktree cleaned up
- [ ] Agent monitor panel in Training nav (post A-016/A-017)
- [ ] Tile grid for agent slots; click → detail overview
- [ ] Open/focus Hyprland window for that agent's live session; document window rules/classes
- [ ] Left assignment list; preselect from A-017 handoff deep-link
- [ ] Actions: assign existing idle agent or create/launch new slot with settings
- [ ] Launch path always yields a visible window + paste-ready or auto-pasted prompt
- [ ] Interactive queue board reflecting disk QUEUE/SESSION without lying
- [ ] ADR; tests where feasible; PROGRESS; HOST note; SESSION; QUEUE/INDEX → done

## Done this session (evidence)
- A-017 (Training Assignments panel) picked up mid-flight from Codex (out of tokens),
  finished, 127 Python tests + all 4 JS suites pass, merged into main at d18da1c, worktree
  and branch (local + remote) removed.

## Next action (one concrete step)
- Set up isolated worktree for A-018, read brain/training.py's slot code + overlay/training.js
  once, then implement the tile grid and Hyprland window launch/focus path.
