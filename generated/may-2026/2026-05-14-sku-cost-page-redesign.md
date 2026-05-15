---
title: Databricks SKU Cost page redesigned with deployment and engine views
date: 2026-05-14
products: [databricks-app]
tag: improved
emoji: 💰
draft: true
description: The SKU Cost page picks up cost trends grouped by serverless / provisioned and by Photon / standard engine, alongside a refreshed cost breakdown view.
---

The SKU Cost page in the Databricks App ships a refreshed layout with two new cost-trend cards: spend grouped by deployment type (**serverless vs provisioned**) and by engine type (**Photon vs standard**). Pair them with the existing SKU breakdown and you can answer "are we burning more on serverless than provisioned this month" without exporting to a spreadsheet.

Cost breakdown by product also gets a measurable perf bump on tenants with long histories, so the page reaches first paint sooner on multi-quarter date ranges.
