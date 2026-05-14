---
title: ClickHouse and MongoDB join Altimate Code's driver list
date: 2026-03-30
products: [altimate-code]
tag: new
emoji: 🗄️
draft: true
description: Altimate Code now talks to ClickHouse (the 12th driver) and MongoDB (the 11th) — schema inspection, query history, and dbt profile mapping all wired up.
---

Altimate Code picks up two more first-class database drivers. **ClickHouse** support arrives as the 12th driver, with password / connection-string / TLS / mTLS authentication, ClickHouse Cloud and self-managed both covered, schema inspection, query-history finops, and dbt profile mapping all integrated. **MongoDB** lands as the 11th driver — full MQL surface (`find`, `aggregate`, CRUD, indexes, collection management), BSON-aware serialization (ObjectId, Decimal128, UUID, Binary), and schema introspection via document sampling.

Both drivers register through the same `Connector` interface as the rest, so the new sources work everywhere the existing ones do — auto-discovery, query commands, schema browsing, and lineage included.
