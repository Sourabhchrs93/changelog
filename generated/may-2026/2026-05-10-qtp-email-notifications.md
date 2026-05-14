---
title: Query Timeout Predictions can now arrive by email
date: 2026-05-10
products: [snowflake-app]
tag: new
emoji: 📧
draft: true
description: Customers without Slack can now receive QTP main-channel timeout alerts by email — with proper thread continuity across follow-up replies.
---

Query Timeout Prediction can now deliver its main-channel alerts over email, alongside or instead of Slack. Customers without Slack — or who want a parallel paper trail — get the same prediction context (workload metadata, projected cost, ready-to-run cancel command) in their inbox.

Threading uses standard email headers so a single timeout prediction stays as one thread in the recipient's inbox even across follow-up replies, the way Slack threads keep a debug discussion together. Debug and reporting channels remain Slack-only for now.
