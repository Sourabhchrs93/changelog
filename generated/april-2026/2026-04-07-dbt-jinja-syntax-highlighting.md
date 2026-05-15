---
title: dbt-aware syntax highlighting for SQL+Jinja and YAML+Jinja
date: 2026-04-07
products: [dbt-power-user]
tag: improved
emoji: 🎨
draft: true
description: Dedicated syntax highlighting for dbt SQL+Jinja and YAML+Jinja, so `ref`, `source`, `config`, and Jinja blocks each get their own colors.
---

dbt Power User now ships dedicated syntax highlighting for dbt SQL+Jinja and YAML+Jinja. `ref`, `source`, `config`, SQL aggregates, window functions, and Jinja `{{ }}` / `{% %}` / `{# #}` blocks each get distinct colors. Schema YAML files highlight Jinja inline alongside YAML, and SQL files no longer fall back to a generic grammar that mis-colored half the keywords.
