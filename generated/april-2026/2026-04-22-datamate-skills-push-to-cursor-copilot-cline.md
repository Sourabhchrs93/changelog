---
title: Datamate Skills push to Cursor, Copilot, and Cline
date: 2026-04-22
products: [datamates]
tag: new
emoji: 📚
draft: true
description: Skills configured on a Teammate now deliver as Cursor `.mdc`, Copilot `.instructions.md`, or Cline `.clinerules/skills/<id>/SKILL.md` files to your workspace automatically.
---

Datamate Skills are push-based markdown instructions that tell an AI agent when and how to use Datamate MCP tools. The MCP server now reads each Teammate's skills and lands them in the right format for whichever IDE you're running — Cursor, Copilot, and Cline are all supported, with conditional activation so each skill only applies to the files it's scoped to.

Custom skills count toward the per-Teammate budget shown on the DatamateCard alongside Assists and Guardrails, and skills marked "always active" attach to every conversation regardless of which file you're editing.
