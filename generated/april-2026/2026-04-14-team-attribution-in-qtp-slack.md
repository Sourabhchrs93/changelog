---
title: Team attribution in QTP Slack threads
date: 2026-04-14
products: [snowflake-app]
tag: improved
emoji: 👥
draft: true
description: Query Timeout Prediction Slack threads now show the owning team even when the query tag is missing — using your tenant's ownership rules as a fallback.
---

When QTP posts a long-running query to Slack, the alert now identifies the owning team even on queries that don't carry a `team` tag. Your tenant's existing ownership rules apply as a fallback whenever the query tag itself is missing.

Tag-derived team always wins when present; the rules engine only fills the gap, so existing tagging conventions keep working unchanged.
