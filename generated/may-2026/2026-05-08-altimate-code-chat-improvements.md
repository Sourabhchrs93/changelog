---
title: Altimate Code chat — codelens framework, split-view, prefill messages
date: 2026-05-08
products: [datamates, altimate-code, dbt-power-user]
tag: improved
emoji: ✨
draft: true
description: Inline codelens prompts above Python data patterns, a side-by-side chat option, prefilled messages you can edit before sending, and migration of DataPilot SQL chat into the Altimate Code submenu.
---

The Altimate Code chat panel picks up four shippable improvements this week. A new **codelens framework** surfaces clickable Datamate actions inline above common Python data patterns — click one and the chat panel opens with a templated prompt prefilled with the matched snippet, the file path, and verb-specific guidance. New detectors can be added without touching the prompt-building code.

The chat panel can now open **beside** the active editor in a split view instead of taking over the editor group, so a SQL file stays visible on the left while the chat runs on the right. A new **prefillMessage** option loads text into the input bar without auto-submitting, so editors and codelenses can stage a prompt for the user to review before sending.

In dbt Power User, the five DataPilot SQL chat commands (**Ask**, **Explain**, **Optimize**, **Change**, **Translate**) migrate into the **Altimate Code** submenu and open chat sessions through the unified chat panel. Translate also picks up a two-step dialect picker.
