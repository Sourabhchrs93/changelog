---
title: dbt Models filter — Integration → Environment cascade
date: 2026-05-08
products: [dbt-power-user]
tag: improved
emoji: 🧰
draft: true
description: The dbt Models page picks up a horizontal filter bar with a proper Integration → Environment cascade — pick a dbt project, environments narrow automatically.
---

The dbt Models page migrates to the horizontal filter bar already used on Datasets and dbt Jobs, with one important addition: a proper **Integration → Integration Environment cascade**. Pick a dbt integration (Core or Cloud) and the environment dropdown narrows to that integration's environments only — no more cross-referencing two unconnected dropdowns to find the right combination.

The separate "dbt Core Integration" and "dbt Cloud Integration" sections collapse into one combined Integration filter, matching how the dbt Jobs page already worked.
