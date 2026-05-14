---
title: Databricks Jobs detail page — new layout, server-backed filters, breadcrumbs
date: 2026-05-06
products: [databricks-app]
tag: improved
emoji: 🧱
draft: true
description: Job ID and workspace move into the page header, tabs go underlined, and Jobs filters become search-as-you-type. Breadcrumbs now follow the full nav stack on every Databricks page.
---

The Databricks Jobs detail page picks up a cleaner layout. Job ID and Workspace move from a separate config card into title sub-headings in the header row; the tab bar drops its pill style and `Card` wrapper for underlined tabs matching the Snowflake query pages. The high-failure alert badge and the Ask AI button are gone.

Jobs page filters for `job_name` and `creator` switch from a flat 100-option dropdown to server-backed search-as-you-type, with debounced API calls and "See More" pagination — tenants with thousands of jobs or principals are no longer capped at the first 100 options. Breadcrumbs now wire through every Databricks page (Jobs, SQL Warehouses, Queries, Workspaces, Users), so the nav stack is visible on every detail route.
