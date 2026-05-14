---
title: Calendar scheduling works on every warehouse, not just resizable ones
date: 2026-03-30
products: [snowflake-app]
tag: improved
emoji: 📅
draft: true
description: Block and manual warehouse schedules now run on warehouses whose auto-resize is disabled — previously they were silently dropped.
---

Block and manual warehouse schedules now execute on any warehouse, regardless of its auto-resize mode. Previously, warehouses with `auto_resize_mode='disabled'` had their schedules silently dropped — the schedule UI accepted the input, but nothing ever ran. Schedules now apply universally and revert the warehouse to its baseline size when the window ends, so scheduling is no longer locked behind the resizing feature.

Manual-resize mode now gates correctly on warehouse eligibility, so the approval path matches what actually happens on the cluster.
