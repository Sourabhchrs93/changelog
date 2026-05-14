---
title: Built-in skills, AI Teammate training, and prompt enhancement in Altimate Code
date: 2026-03-19
products: [altimate-code, dbt-power-user]
tag: new
emoji: 📚
draft: true
description: 22 built-in skills ship with every release, a learn-by-example training system captures corrections, and a small model rewrites rough prompts into specific ones.
---

Altimate Code's skill subsystem grows up in March. Every install or upgrade now ships **22 built-in skills** — `dbt-develop`, `dbt-test`, `dbt-troubleshoot`, `model-scaffold`, `incremental-logic`, `impact-analysis`, `generate-tests`, `train`, `teach`, and others — installed into a dedicated home directory so user-edited skills stay separate from the canonical builtins. A new `data-viz` skill is included, with a 1,000-line component guide that drives the AI through chart and dashboard composition.

The new **AI Teammate training system** turns "no, use `DECIMAL` not `FLOAT`" into a permanent correction. Correct the agent once, accept "want me to remember this?", and the rule persists across sessions and lands in the team repo via git — so a colleague's `git pull` inherits the same knowledge.

An **AI-powered prompt enhancement** action (default `<leader>i`) sends rough prompts ("fix the auth bug") through a small model to get a sharper version back (the specific file paths, the specific error, the constraint to respect) before it goes to the main model.
