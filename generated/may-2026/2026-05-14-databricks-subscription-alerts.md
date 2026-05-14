---
title: Subscription alerts now work on Databricks
date: 2026-05-14
products: [databricks-app]
tag: new
emoji: 🔔
draft: true
description: Create cost and usage alert rules scoped to Databricks entities — jobs, clusters, warehouses — from the same Subscriptions wizard already used on Snowflake.
---

Subscriptions now support Databricks alongside Snowflake. The Subscription wizard picks Databricks as an entity type, walks through Databricks-specific entity details (job, cluster, SQL Warehouse), and submits a valid rule against the same backend used for Snowflake alerts.

Existing alert delivery channels — Slack, email, webhook — all work the same way. So an Auto Tune apply that overshoots a budget or a cluster that idles past a threshold gets the same alerting treatment Snowflake users have had since launch.
