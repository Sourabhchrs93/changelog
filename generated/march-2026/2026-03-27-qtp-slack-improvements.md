---
title: Query Timeout Prediction Slack alerts get cost estimates and clickable IDs
date: 2026-03-27
products: [snowflake-app]
tag: improved
emoji: ⏱️
draft: true
description: QTP Slack threads now show projected cost at timeout, hyperlink each query ID to Snowsight, and surface workload, team, and pipeline context inline.
---

Query Timeout Prediction Slack alerts get four shippable improvements this month. Each thread now shows a **projected cost at timeout** computed from current concurrent-warehouse activity and your billing config, so a "this query will time out" alert immediately answers "and it will cost us this much before it does".

Query IDs are now clickable links straight to the Snowsight query detail page, the instance name appears as a separate field, and the thread is annotated with workload context parsed from the query tag — Source, Pipeline, Task, Environment, Team, and Owner — so the alert is actionable without leaving Slack. A reply thread also surfaces ready-to-run tips, including a `SYSTEM$CANCEL_QUERY` command for the offending query.
