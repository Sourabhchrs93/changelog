---
title: CTE Profiler — per-CTE timing and row counts in the editor
date: 2026-04-15
products: [dbt-power-user]
tag: new
emoji: ⏱️
draft: true
description: Run a dbt model and the editor decorates each CTE with its wall-clock time, row count, and a hot/warm/cool heat tier so you can find the slow one without leaving the file.
---

The dbt Power User extension now profiles every CTE in a model in one click. The CTE Profiler measures per-CTE wall-clock time and row count against your warehouse and decorates the editor inline (`⏱ 1.7s · 100 rows`). Hot CTEs go red, warm yellow, cool grey; a total time and row count lands at the bottom of the file.

No Altimate API key required — the profiler runs through your existing dbt connection.
