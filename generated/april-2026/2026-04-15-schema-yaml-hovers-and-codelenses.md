---
title: Model hovers and Run/Test codelenses inside YAML schema files
date: 2026-04-15
products: [dbt-power-user]
tag: improved
emoji: 🧰
draft: true
description: Hover any model in `schema.yml` to see its description, columns, and types — and run or test it without switching to the SQL file.
---

YAML schema files in dbt Power User now behave like first-class model surfaces. Hover any model name in a `models:` section or source table in a `sources:` block to see the model's description, columns, and data types as a popup — no need to jump to the `.sql` file to remember what's in it.

Each model entry also gets Run, Test, and Document codelenses inline, so the most common actions are one click away from the schema file you're already editing.
