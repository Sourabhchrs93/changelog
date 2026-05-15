---
title: Auto-suspend savings shown as a range
date: 2026-04-14
products: [snowflake-app]
tag: improved
emoji: 💰
draft: true
description: Warehouse auto-suspend savings now report a min/max range that accounts for Snowflake's 30-second polling delay.
---

Warehouse auto-suspend savings now report a range instead of a single point estimate. Snowflake polls for suspendable warehouses roughly every 30 seconds, so the actual suspend happens between 0 and 30 seconds after the `auto_suspend` timer fires. The recommendation card shows both the best case (immediate suspend) and the expected case (mid-poll, +15s) so the savings number isn't optimistic by 15 seconds of runtime per cycle.
