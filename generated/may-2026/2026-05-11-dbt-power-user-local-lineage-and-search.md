---
title: Local column-level lineage by default, plus dbt Models search restored
date: 2026-05-11
products: [dbt-power-user]
tag: improved
emoji: 🔗
draft: true
description: Column-level lineage now runs through the local SQL engine out of the box (no Altimate API call required), and the dbt Models filter bar gets its search input back.
---

Column-level lineage in dbt Power User now defaults to the local SQL engine. New installs and users who never set the lineage engine explicitly get local-first computation — faster, no Altimate API call, and the existing fallback to the legacy path still kicks in transparently when the native module isn't available or the local engine can't resolve a model.

The new horizontal filter bar on the dbt Models page also gets its **search input** back. When the new-filters flag was on, models could only be filtered by category, not searched by keyword — fixed in this release. URL-restored filters no longer flicker on reload, and the Integration Environment dropdown populates correctly even when an integration hasn't been selected yet.
