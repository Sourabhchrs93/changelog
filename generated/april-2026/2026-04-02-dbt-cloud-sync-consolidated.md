---
title: dbt Cloud sync, 5x faster
date: 2026-04-02
products: [dbt-power-user, datamates]
tag: improved
emoji: 🧰
draft: true
description: dbt Cloud sync consolidates ~1000 daily tasks per project/environment into a single ingestion run, cutting sync time from ~250 min to under 50.
---

dbt Cloud sync no longer creates one ingestion task per dbt Cloud run. It now consolidates to a single ingestion per `(project, environment)` per cycle — so a project firing 1000 runs a day produces one ingestion instead of 1000 redundant ones.

A typical 4-worker sync drops from ~250 minutes to under 50.
