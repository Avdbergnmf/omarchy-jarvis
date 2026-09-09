```yaml
id: feat-open-youtube
title: Open YouTube webapp
area: actions
status: unvalidated
jarvis_version_shipped: "0.4.x"
steps:
  - "Press Super+Shift+J"
  - "Type: open youtube"
  - "Approve with Run"
  - "Confirm YouTube opens (or focuses, if already open) in a webapp browser window"
expected: "YouTube opens as a webapp window; running it again focuses the same window instead of opening a second one"
last_human_run: null
notes: "Works even if no local .desktop shortcut for YouTube exists — open_webapp always launches the URL directly."
```
