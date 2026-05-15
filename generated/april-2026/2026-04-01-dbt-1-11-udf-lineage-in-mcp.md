---
title: dbt 1.11 UDF lineage in Datamates MCP
date: 2026-04-01
products: [datamates]
tag: new
emoji: 🔗
draft: true
description: User-defined functions from dbt 1.11 now appear as first-class nodes in lineage graphs served through MCP.
---

Datamates MCP now parses dbt 1.11 function nodes and serves them as first-class lineage nodes alongside models, sources, and exposures. UDFs registered in a dbt project show up in lineage queries automatically — no new MCP tools, no configuration. Projects on older dbt versions see no change; the parser produces an empty map and falls through.
