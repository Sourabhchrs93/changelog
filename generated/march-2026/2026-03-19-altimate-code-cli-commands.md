---
title: New Altimate Code commands — discover, feedback, check, configure-claude/codex
date: 2026-03-19
products: [altimate-code]
tag: new
emoji: ⌨️
draft: true
description: A data-stack scanner, a feedback channel that opens a GitHub issue, a deterministic SQL check command, and bridges into Claude Code and Codex.
---

Altimate Code picks up several new commands in March. **`/discover`** runs a `project_scan` that finds dbt projects, warehouse connections from your dbt profiles or Docker config, and installed tools — then walks you through a five-step setup: scan, review, add connections, index schemas, show next steps. It replaces the old `/init` command, which only generated an `AGENTS.md` file.

**`/feedback`** opens a guided four-step submission that lands as a GitHub issue with `user-feedback` labels, captures CLI version, platform, and OS, and optionally attaches anonymized session context. **`altimate-code check`** runs deterministic SQL checks against `.sql` files without an LLM — 26 lint rules, SQL safety / injection detection, validation, policy, and PII scanning — JSON-formatted output suitable for CI.

Two bridge commands — **`/configure-claude`** and **`/configure-codex`** — write the right config so `/altimate` works as a slash command inside Claude Code, and Codex CLI picks up Altimate Code as a skill.
