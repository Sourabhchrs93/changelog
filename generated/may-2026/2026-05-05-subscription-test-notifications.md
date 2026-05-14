---
title: Test subscription delivery before saving the rule
date: 2026-05-05
products: [snowflake-app, databricks-app, datamates]
tag: improved
emoji: 🔔
draft: true
description: A working "Send preview to destination" button in the subscription rule editor — confirms the alert lands in the right inbox or Slack channel before the rule goes live.
---

The "Send preview to destination" button in the subscription rule editor is now functional. Click it before saving and the rule runs a real evaluation against your data and delivers the resulting alert to the configured destinations, so a misconfigured Slack webhook or a typo'd email recipient is obvious immediately.

Per-channel success or failure surfaces in a toast — the rule editor reports each destination separately, so a working Slack channel and a misconfigured email are flagged distinctly.
