---
title: Custom tag filter dropdowns on the Workloads page
date: 2026-03-02
products: [snowflake-app, databricks-app]
tag: improved
emoji: 🔎
draft: true
description: Any custom tag configured on a tenant now becomes a filter dropdown across Custom Workloads jobs, graph, and Snowflake Jobs views.
---

The Workloads page picks up filter dropdowns for every custom tag configured on your tenant. The Custom Workloads jobs table, the Workloads graph, and the Snowflake Jobs view all share the same set of dynamic tag filters, so a tenant that tags queries by `team`, `cost-center`, and `pipeline` gets three new filter dropdowns under "More Filters" with one selection driving both the table and the chart.

The custom-tag selections also participate in the URL, so a filtered view is shareable as a link.
