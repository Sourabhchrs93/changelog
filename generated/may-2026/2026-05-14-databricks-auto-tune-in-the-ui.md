---
title: Databricks Auto Tune is now available in the UI
date: 2026-05-14
products: [databricks-app]
tag: new
emoji: 🤖
draft: true
description: A dedicated Auto Tune tab on every Databricks job, an apply flow tied to the actual worker, single-job cost trends, and a rollback note so nobody is surprised.
---

Databricks Auto Tune now has a UI. Open any job and the new **Auto Tune** tab on the detail page shows the current recommendation, the proposed cluster shape, and a card that drives a four-state flow — proposed → enabled → applied → rolled back — wired directly to the apply worker's audit log so the UI reflects what actually happened on the cluster, not what we wished had happened.

The job's run-trend chart picks up cost alongside duration and success rate, so the value of an Auto Tune apply is visible from the same screen on the next run. The drawer banner adds an explicit rollback note: _"Recommendations will be rolled back if a job's execution time exceeds 1.5x its baseline"_ — so teams know the safety net before they enable it. The Auto Tune toggle now renders even when a preflight check blocks apply, so a misconfigured workspace surfaces an actionable error instead of an invisible switch.
