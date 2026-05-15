---
title: Databricks Jobs, Spark analysis, and Users deep-dive
date: 2026-04-22
products: [databricks-app]
tag: new
emoji: 🧱
draft: true
description: Run trends, Spark stage-level analysis, user attribution, and a dedicated Databricks summary.
---

The Databricks App now drills down to the rows that explain a job's cost: a Jobs page with success/failure run trends and per-job duration and cost; a Spark analysis surface with stage-level gantt charts, task drill-downs, and config tabs; and a Users page with per-user cost attribution and a summary chart.

A Databricks-specific Summary page replaces the Snowflake layout for Databricks tenants — workspace cost moves to the top of the sidebar, and the navigation hides Snowflake-only sections that didn't apply. Open a job to follow it from run trends → stages → tasks → individual run, without losing the cost context on the way down.
