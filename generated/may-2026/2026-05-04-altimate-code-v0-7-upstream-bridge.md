---
title: Altimate Code v0.7 — upstream OpenCode v1.4.0 in the box
date: 2026-05-04
products: [altimate-code]
tag: improved
emoji: 🚀
draft: true
description: Altimate Code v0.7 bridges upstream OpenCode v1.4.0 — picking up upstream improvements while keeping all the altimate-specific features intact.
---

Altimate Code v0.7 bridges to upstream OpenCode v1.4.0. The upstream history was rewritten between v1.3.17 and v1.4.0, so this release uses a one-off bridge merge that overlays v1.4.0 while preserving every altimate-owned feature — the skills subsystem, the AI Teammate training system, the warehouse drivers, and the three-mode runtime all carry across unchanged.

Run `altimate upgrade` to pick it up. The `altimate-code` alias still resolves, so existing scripts keep working as-is.
