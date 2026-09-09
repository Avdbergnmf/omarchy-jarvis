---
name: scratch-and-mail
description: Move the focused application to scratchpad and open Outlook when asked to scratch a window and open email.
---

# scratch-and-mail

Run scratch_move_here, then open_webapp for Outlook. Focus the intended application first; moving it hides it in special:scratchpad. SUPER+S reveals it again.

Execute `./run.sh` from this directory, or `actions/run_skill scratch-and-mail` from the repository root. Preview with `./run.sh --dry-run`. Output is JSON lines; a nonzero exit stops the recipe and reports partial progress.

Triggers: “move this window to scratchpad and open email”, “scratch and Outlook”.

Safety: opens/focuses webapps only; does not send messages or modify account data. These examples were explicitly requested; future generated skills stay in drafts until the user approves promotion.
