---
title: dbt 1.11 UDFs appear in lineage as first-class nodes
date: 2026-03-13
products: [dbt-power-user, datamates]
tag: new
emoji: 🔗
draft: true
description: User-defined functions (UDFs) from dbt 1.11 now show up in lineage graphs alongside models, sources, and exposures — with arguments and return types on the detail panel.
---

dbt 1.11's new function (UDF) resource type now renders as a first-class node in the lineage view. Functions appear in graphs whenever they're upstream or downstream of models, the detail panel shows arguments (not "columns") with data types and descriptions, and a separate "Returns" section shows the function's return type below the arguments.

The materialization label shows the function flavor — for example, "scalar function" — instead of the raw config value. Function `.py` files are recognized as lineage entry points, so opening a UDF's Python file is now a valid way to start exploring upstream dependencies.
