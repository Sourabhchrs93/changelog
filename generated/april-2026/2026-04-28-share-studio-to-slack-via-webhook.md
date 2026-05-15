---
title: Share Studio sessions to Slack
date: 2026-04-28
products: [snowflake-app, databricks-app]
tag: new
emoji: 💬
draft: true
description: Send a Studio session or scheduled report into any Slack channel using an incoming webhook — no OAuth, no admin setup.
---

Studio's Share dialog now has a Slack tab. Paste an incoming-webhook URL once and the same session, with answer and inline charts, posts into the destination channel. The Schedule dialog supports the same webhook target, so recurring reports can land in a Slack channel on a cadence without anyone configuring an integration.

No OAuth, no bot tokens, no settings page — the share flow reuses the same notification webhook plumbing that drives alerts and scheduled reports.
