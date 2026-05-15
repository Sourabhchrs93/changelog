---
title: Alerts — searchable tags filter and a saner default schedule
date: 2026-03-18
products: [snowflake-app, databricks-app, datamates]
tag: improved
emoji: 🔔
draft: true
description: Tag filters on query alerts now search-as-you-type across 100K+ values, and the default alert delivery time moves from 9 AM to 2 PM UTC.
---

Query alerts pick up two improvements. The Tags filter on the Query entity is now search-as-you-type: tenants with 100K-plus distinct query tags no longer hit a frozen picker, because the filter paginates server-side and only loads what the user is searching for.

The default schedule for newly created alerts also moves from 9 AM UTC to **2 PM UTC**, lining up better with North American working hours. Existing alerts keep whatever schedule you set them to.
