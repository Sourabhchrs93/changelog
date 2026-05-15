---
title: dbt Cloud environment aliases
date: 2026-04-06
products: [dbt-power-user]
tag: improved
emoji: 🧰
draft: true
description: Map differently-named dbt environments to the same logical environment so warehouse data lines up with model data.
---

dbt Cloud environments can now carry aliases. If your warehouse refers to "Prod" but your dbt Cloud environment is "Production_5505", set an alias and both names resolve to the same logical environment — no more disjoint joins or missing model rows on the warehouse side.

Multiple aliases per environment are supported; setting none leaves behavior unchanged.
