---
title: Studio reports and sessions — schedules list, archive, PDF attachments
date: 2026-05-11
products: [snowflake-app, databricks-app, datamates]
tag: improved
emoji: ✨
draft: true
description: A View-all-schedules button in the Studio sidebar, archive and delete on Studio sessions, PDF report attachments on scheduled emails, and a redesigned report email with the Studio palette.
---

Several Studio session and report improvements landed together. A **View all schedules** icon button sits next to the sidebar search, opening the schedule dialog directly into a list of every schedule across all sessions — no longer scoped to the open session.

Studio sessions now support **archive** and **delete** from the sidebar: archive hides a session without losing it (restore from the archived view), and delete soft-deletes with a recovery window before it goes for good. Each session also carries a one-line intent shown in the sidebar so a long-running conversation is identifiable at a glance.

Scheduled report emails arrive with the report attached as **`studio-report.pdf`** so the body content is portable beyond email. The email body itself gets a redesigned template using the Studio palette and a card-style layout that reads cleanly across Gmail, Apple Mail, and Outlook. The Schedule action moves from the page header to the chat message footer next to Download, so creating a recurring report happens from the same row as exporting a one-off.
