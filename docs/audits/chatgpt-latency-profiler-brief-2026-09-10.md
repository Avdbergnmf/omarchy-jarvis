# ChatGPT brief: Jarvis Text Latency Profiler (2026-09-10)

Alex pasted this from ChatGPT. Desk split it into Wave 1 assignments **A-033 → A-035** (after A-032 + Wave 0).

## Intent (desk summary)
Text-first only (no voice/VAD/TTS). Unity-Profiler-inspired Training view answering: how responsive does it feel, where did time go, did a change help/hurt. OTel-like spans, lightweight local store, privacy-first (timings default; content not auto-persisted). Primary metric: **meaningful reaction latency** (submit → first visible meaningful output), not TTFT alone. Extend existing journal/events where clean; core emits traces, Training UI consumes. Canonical span vocabulary. Instrument from Enter, not only model call. Parallel spans; percentiles; version compare; ledger hooks later.

See A-033/A-034/A-035. Do not implement the entire brief in one PR. Full ChatGPT prose was provided in the JARVIS room; this file is the operational summary for agents without chat history.
