---
title: Altimate Code auto-discovers MCP servers from your existing tools
date: 2026-03-21
products: [altimate-code]
tag: improved
emoji: 🔌
draft: true
description: MCP server configs from Cursor, Claude Code, GitHub Copilot, and Gemini are loaded automatically at startup — no manual copy-paste.
---

Altimate Code now reads your existing MCP server configuration at startup from Cursor's `.vscode/mcp.json`, GitHub Copilot's `.github/copilot/mcp.json`, Claude Code's `.mcp.json`, and Gemini's settings file — and registers them at the lowest priority, so your own Altimate Code config always wins.

A new `/discover-and-add-mcps` command writes the discovered servers permanently to either project or global scope when you're ready to commit. JSONC comments in the source configs are preserved, and remote vs local server transforms happen automatically.
