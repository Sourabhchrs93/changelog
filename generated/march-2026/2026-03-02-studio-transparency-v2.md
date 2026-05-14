---
title: Studio answers now show inline data provenance
date: 2026-03-02
products: [snowflake-app, databricks-app, datamates]
tag: new
emoji: 🔍
draft: true
description: Every significant number in a Studio answer carries a clickable marker showing the data source, query, and computation behind it.
---

Studio answers now show inline data provenance. Every significant number in the response carries a small marker; click it to see the data source, the query that produced it, and the computation steps used to derive it.

The annotations are produced by a separate analysis pass that runs after the answer is generated — so the answer text itself is never rewritten, and the lineage you see in the popover matches what the model actually computed. Numbers that can't be traced (model commentary, narrative summaries) carry no marker, which makes the cited values stand out.
