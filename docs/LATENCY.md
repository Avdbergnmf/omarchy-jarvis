# Latency profiler (A-033)

Text-first diagnostic timings for one submitted overlay message. Training **Latency**
(A-034) is a history + waterfall on this store. Not percentiles (A-035), not an SLO.
Core emits traces; nothing here auto-stores prompts or payloads.

Primary metric: **`meaningful_response_latency`** = submit → first *visible meaningful*
content. "Thinking…" / "Planning your request…" are **ack**, not meaningful. TTFT
(`model.chat` return) is recorded for diagnosis and is **not** the product number.

## Canonical span vocabulary

| name | what |
|---|---|
| `interaction` | root; one submitted message (`trace_id` linked to `run_id`) |
| `http.request` | unused in v0 (receipt is `interaction` start) |
| `route` | `route_prompt` (deterministic) |
| `ack` | first placeholder the user can see |
| `plan` | `json_plan` / tools plan / intake / correction / fixed plan |
| `model.chat` | one Ollama `/api/chat` round trip |
| `commit_plan` | unused as a named span in v0; the function still marks meaningful |
| `await_approval` | reserved; wall-clock waiting is not the product metric |
| `execute` | approved tool loop |
| `tool` | one action; `attrs.tool` is the name only |
| `persist.journal` | terminal journal writes |
| `overlay.submit` | reserved (client submits via `/v1/run` `client_submit_ms`) |
| `overlay.render.ack` | client POST `/v1/runs/<id>/latency` `mark=ack` |
| `overlay.render.meaningful` | client POST `mark=meaningful` |

Parallel child spans are allowed (two `tool` spans under `execute`). Durations use
`time.monotonic_ns()`.

## Store and privacy

SQLite at `$XDG_STATE_HOME/jarvis/latency/traces.sqlite` (default
`~/.local/state/jarvis/latency/`, mode 0600/0700, gitignored by virtue of living
outside the repo). Override the directory with `JARVIS_LATENCY_DIR`. Bounded to
200 traces. Columns are timings, `run_id`, version, revision, model, planner
mode, span names/attrs. **No prompt, reply, tool arguments, or token-shaped
keys.** Attr names matching those are dropped at span create.

The overlay may POST `ack`/`meaningful` *after* the run has already persisted
(fast chitchat). Finished traces stay in a small in-memory window so those
marks rewrite the store instead of 404ing.

GET `/v1/runs/<id>` polls do not write traces (ADR-018). Marks are POST
`/v1/runs/<id>/latency`. Training **Latency** (A-034) reads `GET /v1/latency/traces`
and `GET /v1/latency/traces/<trace_id>` (token-gated).

## On / off

`~/.config/jarvis/config.toml`:

```toml
latency_profiler = true   # default; false/off/0 disables all recording
```

Restart the brain after changing it. When off, `Tracer` is a no-op and the store is
not opened.

## Overhead

Spans live in memory for the in-flight run. SQLite is written **once** on terminal
status (`done`/`error`/`denied`) inside `release_busy`, not per poll and not per
span. Expected cost is a cheap monotonic read per span start/end plus one short
transaction at the end of the turn.

## Client vs server clock

The overlay stamps `client_submit_ms` on POST `/v1/run` and POSTs `ack` /
`meaningful` marks with `client_ms`. When both submit and meaningful client stamps
exist, `meaningful_response_latency_ns` uses that wall-clock delta (Enter → first
non-placeholder paint). Otherwise it falls back to server monotonic time from
trace start to `mark_meaningful` (first non-placeholder `announce` / plan reply).

## Training UI (A-034)

Training → **Latency**: recent-interaction bars (bar length = MRL) and a click-through
waterfall. Incomplete and error traces stay listed. No prompt/payload display.
Distributions / version compare are A-035.

## Blind spots for A-035

- No p50/p90, version compare, or ledger PERF hook (A-035).
- Approval wait is not a first-class `await_approval` span yet (would dwarf plan
  time and is optional to the product metric).
- `tools_run` follow-up `model.chat` after the tool batch still parents to the
  root interaction, not `execute`.
- Client and server clocks are not NTP-aligned; prefer the client delta when present.
- Overlay restore-on-load does not emit marks (no submit in that session).

## Ledger (proposal only — Desk writes `docs/ledger/`)

If traces show approval-wait or model.chat dominating, Desk may file an IMP later.
This assignment does not allocate an `IMP-*` id.
