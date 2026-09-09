```yaml
id: feat-open-by-name
title: Open any installed app by name
area: actions
status: unvalidated
jarvis_version_shipped: "0.4.x"
steps:
  - "Press Super+Shift+J"
  - "Type: open spotify"
  - "Approve with Run"
  - "Confirm Spotify opens (or focuses, if already running)"
expected: "Spotify window opens and is focused; running it again while Spotify is already open focuses the same window instead of opening a second one"
last_human_run: null
notes: "General mechanism (actions/open_app_by_name) resolves any installed .desktop app by name, not just Spotify — try a second app name (e.g. Discord) if you want broader coverage."
```
