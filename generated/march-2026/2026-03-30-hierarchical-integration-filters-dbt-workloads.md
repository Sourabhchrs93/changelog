---
title: Hierarchical integration filters on dbt workloads
date: 2026-03-30
products: [dbt-power-user, snowflake-app]
tag: improved
emoji: 🧰
draft: true
description: The dbt workloads filter set now groups integrations with their environments — pick a project, narrow to its environments, drill into the right one without typing.
---

dbt workload filters now show integrations grouped with their environments, instead of two flat lists you had to cross-reference manually. Pick a dbt integration and the environment dropdown narrows to that integration's environments only; pick an environment and the integration above it gets selected for you.

For tenants with many dbt projects and short-lived environment names that collide across projects (`Production_5505` is a different environment from `Production_8421`), the grouping fixes the ambiguity at the filter level.
