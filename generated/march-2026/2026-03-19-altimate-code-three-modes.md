---
title: Altimate Code simplifies to three modes — Builder, Analyst, Plan
date: 2026-03-19
products: [altimate-code]
tag: improved
emoji: 🤖
draft: true
description: The CLI consolidates seven agents into three modes, adds SQL write-access control, and hard-blocks DROP / TRUNCATE across the board.
---

Altimate Code's agent model collapses from seven specialized agents to three modes that map cleanly to how people actually use it: **Builder** (the default — writes code and SQL, with destructive writes prompting for approval), **Analyst** (read-only — bash and SQL writes are denied), and **Plan** (proposes a plan without executing).

A new SQL write-access control runs in front of every query. Analyst mode rejects writes outright; Builder mode prompts before letting them through; and `DROP DATABASE`, `DROP SCHEMA`, and `TRUNCATE` are hard-blocked regardless of mode. The permission lives in both the permission system and the SQL executor itself, so a misconfigured permission can't accidentally let a destructive query through.
