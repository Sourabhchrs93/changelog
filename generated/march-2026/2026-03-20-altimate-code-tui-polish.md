---
title: Altimate Code TUI polish — smoother streaming and a shorter binary
date: 2026-03-20
products: [altimate-code]
tag: improved
emoji: ⚡
draft: true
description: Streaming responses render without jumps, the footer shows when an upgrade is available, and the CLI is now invoked as `altimate`.
---

Streaming responses in the TUI no longer jump as the model writes. While a message is streaming the renderer uses a lightweight code-aware path that highlights syntax without re-laying out block elements; once the message finishes it swaps to full Markdown rendering — same end result, much calmer in motion.

The TUI footer now shows a persistent `local → 0.5.0 · altimate upgrade` hint whenever a newer release is available, instead of a 10-second toast you might miss. A post-install welcome banner walks new installs through the next steps, and the CLI itself is now invoked as **`altimate`** — the old `altimate-code` binary stays as a symlink, so existing scripts keep working unchanged.
