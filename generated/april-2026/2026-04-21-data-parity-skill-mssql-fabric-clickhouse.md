---
title: Data-parity diffs across SQL Server, Fabric, and ClickHouse
date: 2026-04-21
products: [altimate-code]
tag: new
emoji: 🔁
draft: true
description: Altimate Code can now diff data across SQL Server / Azure Fabric and ClickHouse with partition-aware execution and seven Azure AD auth flows.
---

Altimate Code's `data_diff` tool now handles three more warehouses end-to-end: SQL Server, Azure Fabric, and ClickHouse — all with partition-aware execution so large tables diff in independent chunks instead of one monolithic scan.

Azure AD authentication is supported for SQL Server and Fabric, covering the common service-principal, MSI, and CLI flows.
