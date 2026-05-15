---
title: Generate dbt unit tests from your manifest
date: 2026-04-13
products: [altimate-code, dbt-power-user]
tag: new
emoji: 🧪
draft: true
description: A new `dbt_unit_test_gen` tool inspects compiled SQL and writes dbt unit tests with type-correct mock data, including incremental and ephemeral cases.
---

Altimate Code now generates dbt unit tests for you. Point it at a model and it reads the manifest and compiled SQL, detects the scenarios that matter (CASE branches, JOINs, GROUP BY, division-by-zero, incremental loads), and writes a `unit_tests:` block in the model's schema YAML with type-correct mock data — happy path, null variants, and boundary cases.

Incremental models also get a prior-state mock so the generated test exercises the merge logic, not just the initial load. Snowflake, Databricks, BigQuery, Redshift, and Postgres are all supported.
