# Feature: Extract mixed Control Plane modules

- **id:** feat-self-improve-control-plane-extraction
- **difficulty:** L
- **status:** open
- **source:** A-030 boundary inventory 2026-09-10
- **wave:** future hardening

## Summary
Separate authorization, grader/oracle, trusted-skill manifest/digest, and deployment-policy
code from today's mixed `brain/`, `actions/`, and `scripts/` surfaces. Use A-030's versioned
inventory as the starting boundary and narrow CODEOWNERS only after physical isolation exists.

## Why later
A-030 needs an honest coarse ownership map now; moving runtime code is a separate architectural
change and must not be smuggled into the policy assignment.

## Acceptance (sketch)
Dedicated modules have explicit APIs and boundary tests; Runtime cannot mutate grader/promotion
policy through ordinary feature paths; the A-030 manifest and CODEOWNERS patterns can become
narrower without leaving any authority-bearing path unclassified.
