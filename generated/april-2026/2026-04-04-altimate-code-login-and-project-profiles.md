---
title: Sign in to Altimate and find project-local dbt profiles
date: 2026-04-04
products: [altimate-code]
tag: new
emoji: 🔐
draft: true
description: A `/login` command for the Altimate provider, plus dbt-standard profile discovery that picks up project-local and `DBT_PROFILES_DIR` paths.
---

Altimate Code's TUI now includes the Altimate platform as a first-class LLM provider. A new `/login` dialog asks for instance name, API key, and URL, validates the credentials before saving, and re-bootstraps the session immediately — no restart, no manual config edits.

dbt profile discovery also catches up to dbt's standard resolution order. `/discover` now finds profiles in priority order: an explicit path argument, `DBT_PROFILES_DIR`, a project-local `profiles.yml` sitting next to `dbt_project.yml`, and finally `~/.dbt/profiles.yml`. The common CI/CD pattern of committing a project-local profile no longer falls back silently to the global one.
