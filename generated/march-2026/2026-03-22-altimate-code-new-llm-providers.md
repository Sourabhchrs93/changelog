---
title: Three new LLM providers — Snowflake Cortex, LM Studio, Anthropic OAuth
date: 2026-03-22
products: [altimate-code]
tag: new
emoji: 🤖
draft: true
description: Snowflake Cortex (billed through Snowflake credits), LM Studio (local Qwen and friends), and an in-tree Anthropic OAuth plugin all join the provider list.
---

Three LLM provider additions land in March. **Snowflake Cortex** ships as a built-in provider; authenticate with a Programmatic Access Token in `<account>::<token>` form and billing flows through Snowflake credits — Claude, Llama, Mistral, and DeepSeek models all selectable. **LM Studio** registers as an OpenAI-compatible provider for local model serving, so a local Qwen run is one config block away.

The third addition is structural: **Anthropic OAuth** is now an in-tree plugin instead of an external npm dependency that didn't exist on the registry. Claude Pro and Max OAuth, OAuth-driven API key creation, and manual API key entry all live in the plugin alongside Codex and Copilot — fewer moving parts, cleaner upgrades.
