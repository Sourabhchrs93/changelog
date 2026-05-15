---
title: Schedule name validation and "Send Now"
date: 2026-04-15
products: [snowflake-app, databricks-app]
tag: improved
emoji: ⏱️
draft: true
description: Auto-generated schedule names now stay under the limit, and a Send Now option fires a scheduled report on demand.
---

Auto-generated schedule names that ran past the 255-character limit no longer fail silently — names are truncated to fit, and the schedule form blocks names over the limit with a clear error instead of a backend rejection.

The schedule "More options" menu also picks up a **Send Now** action, so a report can be fired on demand without waiting for the next scheduled run.
