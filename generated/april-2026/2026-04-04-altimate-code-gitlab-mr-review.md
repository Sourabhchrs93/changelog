---
title: AI code review for GitLab merge requests
date: 2026-04-04
products: [altimate-code]
tag: new
emoji: 🔎
draft: true
description: The Altimate Code CLI fetches a GitLab MR diff, runs the AI review, and posts the result back as MR notes.
---

Altimate Code's CLI now reviews GitLab merge requests end-to-end. Run `altimate-code gitlab review <mr-url>` and the CLI fetches the diff through GitLab REST API v4, runs the AI review, and posts the results back as MR notes — the same flow that has been available for GitHub since launch.

URL parsing handles gitlab.com, self-hosted instances on custom ports, and nested group project paths. A `--no-post-comment` flag dry-runs the review locally, and `--model` picks which model handles the analysis.
