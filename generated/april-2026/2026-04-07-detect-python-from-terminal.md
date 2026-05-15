---
title: One-click fix for "dbt works in terminal but not in the extension"
date: 2026-04-07
products: [dbt-power-user]
tag: new
emoji: 🐍
draft: true
description: A "Detect Python from terminal" action finds the Python interpreter where dbt actually lives and points the extension at it.
---

The most-reported onboarding bug — dbt works in your terminal but not in the extension because VS Code's Python extension picked a different interpreter — now has a one-click fix. The new **Detect Python from terminal** action runs through your login shell to find where `dbt` actually lives and writes that path into the extension's Python override.

The button appears on every Python or dbt error dialog and in the onboarding prerequisites step, so the failure mode that used to require Stack Overflow now resolves in seconds.
