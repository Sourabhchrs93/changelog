---
title: Subscriptions — webhooks, cloning, team alerts, same-weekday comparisons
date: 2026-04-14
products: [snowflake-app, databricks-app, datamates]
tag: improved
emoji: 🔔
draft: true
description: Webhook delivery, one-click clone for any alert, team-level cost alerts, and same-weekday comparison for warehouse metrics.
---

Subscriptions picks up four shippable improvements this month. Webhooks join Slack and email as a first-class delivery channel — paste a URL into any rule and get a typed JSON payload with tenant, timestamp, and a deep-link back to the dashboard. Clone duplicates any alert or report you own in one click; the copy lands in the wizard ready to edit.

Team is now a first-class entity in alerting, so a rule like _"total daily cost for team data-products > $100"_ works without per-warehouse plumbing. The new same-weekday comparison mode compares today against the prior week's same day — much better for warehouses with weekly seasonality than the old day-over-day baseline. Tag filters in the wizard switched to server-side search, so high-cardinality tag spaces no longer freeze the picker.
