---
name: changelog-month
description: Generate the full monthly changelog draft — fetch releases across all 8 source repos, triage features, consolidate clusters, write polished entries to generated/<month>/, validate, commit to a branch, and create a Notion review page. Use after a month closes to produce ~15-25 draft entries for team review. Invoke as `/changelog-month 2026-04` or `/changelog-month` and answer prompts.
---

# Monthly changelog draft

You are generating a full month of customer-facing changelog entries for the Altimate Platform. The input is a month identifier; the output is a branch with ~15-25 polished draft entries, validated against the CI schema, plus a Notion review page for the team.

This skill is a **multi-phase recipe**. After each phase, summarize what happened and confirm with the user before moving on — do not run end-to-end in one go without checkpoints.

## Read first

Before phase 1, read in order:

1. `STYLE.md` — voice and tone rules.
2. `products.yml` — closed list of product slugs and `allowed_hosts`.
3. The most recent 3-5 files in `entries/` to ground the voice.
4. `scripts/build_features.py` — to understand the classifier and dedup logic the triage uses.
5. **The "Trim rules" section below** — reviewer-confirmed patterns to apply preemptively.

## Inputs

Look at the invocation. The user may have given you:

- A month identifier `YYYY-MM` (e.g. `2026-04`) — use it as the window.
- Nothing — ask: "Which month? (YYYY-MM format)"

Resolve the date window:
- For a full month: `WINDOW_START = YYYY-MM-01`, `WINDOW_END` = last day of month (28-31 depending).
- For the current month (month-to-date): `WINDOW_END` = today's date.

## Phase 1 — Setup

1. Run `git status --short`. If there are uncommitted changes that don't belong to this work, stop and ask the user what to do — never wipe their work.
2. Switch to `main` and pull (`git checkout main`). Branch off as `feat/<month>-2026-changelog-drafts` (e.g. `feat/april-2026-changelog-drafts`).
3. Check if `scripts/` and the `.gitignore` updates exist on `main`:
   - If they do: continue.
   - If they don't (typical — only on the per-month branches): restore them from the most recent existing month branch with `git checkout feat/<prior-month>-2026-changelog-drafts -- scripts/ .gitignore`. If no prior month exists, ask the user to point at the branch that has the scripts.
4. Confirm the working tree has: `scripts/{fetch_releases,fetch_pr_bodies,build_features,build_curation,polish_entries,generate_entries,reparse_releases}.py`.
5. Print a one-line summary and ask: "Branch ready. Proceed to fetch?"

## Phase 2 — Fetch releases + PR bodies

1. Run `scripts/fetch_releases.py --since <WINDOW_START> --out data/releases_<month>.json`. Note the per-repo release counts — if any repo returns 0 for a full month, flag it (might indicate a fetch regression).
   - **Sources in scope (8 repos):** `altimate-backend`, `altimate-frontend`, `vscode-dbt-power-user`, `altimate-code`, `altimate-core`, `altimate-mcp-engine`, `vscode-altimate-mcp-server`, `altimate-dbt-snowflake-query-tags`. The full list with primary-product mapping lives in `scripts/fetch_releases.py::REPOS`.
   - **`altimate-core` is a published library** (powers Altimate Code's SQL engine). Its release bodies are install/deploy artifacts, not PR lists. The fetcher uses the `REPOS_NEEDING_COMPARE_FALLBACK` set + GitHub compare API to enumerate PRs between consecutive tags from commit messages — same downstream shape, just sourced differently. Don't be surprised by low PR counts; altimate-core typically only sees a handful of feature PRs per release.
2. Run `scripts/fetch_pr_bodies.py --releases data/releases_<month>.json --out data/prs_<month>.json --workers 8`. Use `run_in_background` if expected total > 500 PRs — the GraphQL fetch is ~12 PRs/sec.
3. Print totals: releases per repo, total PRs.
4. Ask: "Fetched N releases / M PRs. Proceed to triage?"

## Phase 3 — Triage

1. Write or reuse a `scripts/<month>_triage.py` (clone of `march_triage.py` with the date window updated). It must:
   - Filter `pr_release_idx` to the WINDOW_START..WINDOW_END inclusive.
   - Use `primary_product` from each repo (the new-repo classifier lookup) so dbt-power-user / altimate-code / datamates entries get product tags even when keywords don't match.
   - Apply `feat:` prefix + Jira dedup + paired-PR dedup + trivial filter from `build_features.py`.
   - Apply the SHIP/SKIP regex patterns documented at the bottom of `march_triage.py`.
2. Run it. Write `data/features_<month>.json`.
3. Print the triage table grouped by week. Highlight:
   - **SHIP** — clear customer-visible features (~15-30 typically).
   - **REVIEW** — your call (~10-30 ambiguous, often the most interesting).
   - **SKIP** — internal infra, schema migrations, model routing, analytics tracking.
4. Ask the user to:
   - Confirm or modify the SHIP list (add from REVIEW, remove from SHIP).
   - Decide on REVIEW items.

## Phase 4 — Consolidate

Before writing entries, group SHIP+approved-REVIEW into **feature clusters**. The customer changelog rate is ~10-20 polished entries per month — so 50+ atomic SHIP items must consolidate.

**Cluster patterns observed across April / March / May 2026:**

| Cluster | Typical members |
|---|---|
| **Auto Tune launch / improvements** | Auto Tune tab, apply flow, cost trends, rollback note, preflight toggle, UI feedback — combine into one launch entry |
| **Studio reports/sessions** | scheduled-report email redesign, archive/delete, View-all-schedules button, PDF attachment, Schedule-button reposition — combine |
| **Databricks page launches** | Users page, Jobs page, Spark analysis, sidebar, summary page (when in same week) — one launch entry per the existing `2026-01-16-databricks-full-platform-support.md` pattern |
| **Databricks Jobs page polish** | layout refresh + breadcrumbs + API-backed filter dropdowns (same week) — combine |
| **Subscriptions enhancements** | webhook delivery, clone alert, team-as-entity, same-weekday comparison, searchable tags, default schedule change, test-notification — combine |
| **Cortex AI services** | usage history additions for new Cortex surfaces, warehouse-name fix — combine |
| **Altimate Code subsystem release** | new commands + new providers + new drivers + skill system updates in same window — one entry per subsystem (commands / providers / drivers / skills / TUI polish) |
| **Altimate Code SQL engine (`altimate-core`)** | new lint rules, new validators, new safety checks, new PII detectors — combine per category. Many altimate-core releases are version bumps with no shippable feature content; only write an entry when there's a customer-visible change. |
| **dbt 1.11 UDF lineage** | cross-repo backend MCP + extension lineage view — one entry |
| **Referral program** | signup UI + backend credit grant + admin codes page — one entry |
| **Email + report redesigns** | template + delivery + content — combine if same week |

**When to consolidate:**
- Same theme, ships within 1-2 weeks → one entry.
- Cross-repo (backend + frontend or BE + extension) with shared Jira → one entry.
- Multiple PRs flagged "Studio" / "Auto Tune" / "Subscriptions" → one entry per theme.

**When to keep separate:**
- Two different products (`databricks-app` vs `snowflake-app`) doing analogous work.
- Same theme but more than ~3 weeks apart.
- One is a launch entry, others are post-launch polish on a different surface.

Print the consolidation plan as a numbered list with the merged title, products, tag, source PRs. Ask the user to confirm or adjust.

## Phase 5 — Write entries

For each cluster, write a file at `generated/<month>-2026/YYYY-MM-DD-<slug>.md`. The date is the **latest** ship date in the cluster.

### Frontmatter

- `title` ≤80 chars, names the feature (not a verb phrase like "Added X").
- `date` matches filename.
- `products` only from `products.yml` (closed list).
- `tag`: `new` for net-new, `improved` for enhancements to existing features, `beta` for gated/opt-in.
- `emoji` — single emoji per the category map in `changelog-add` SKILL.
- `draft: true` — ALWAYS. Never publish straight to `entries/`.
- `description` ≤180 chars, one sentence of user benefit.

### Body — voice rules

Start every body with the **user benefit**, not the implementation. One paragraph, two short ones max. Aim for 60-150 words.

### Trim rules (apply preemptively — these are reviewer-confirmed)

Strip the following kinds of content from every entry, even when the source PR description includes them. These are non-negotiable; failing to strip these is the #1 reason an entry reads as engineering notes instead of product copy.

**Drop these unconditionally:**
- **Internal endpoint paths** — `/auth_health`, `/payment/token-usage`, `/chat/completions`, `/mcp`, `/sse`, `/studio/session_to_pdf`. Replace with plain-English ("the agent gateway", "the chat panel").
- **File extensions for IDE config** — `.mdc`, `.instructions.md`, `.clinerules/skills/<id>/SKILL.md`. Say "in the right format for each IDE".
- **Environment variable names** — `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DBT_PROFILES_DIR` (except `DBT_PROFILES_DIR` which is a dbt-standard name users know; that one stays).
- **Credential formats** — `host::token`, `<account>::<token>`. Say "personal access token" or "API key".
- **File-permission octals** — `0600`. Drop.
- **Internal file paths** — `~/.altimate/altimate.json`. Drop.
- **Tool/class names from the codebase** — `Typography`, `dbt_unit_test_gen`, `WebhookPayload`, `EmailNotifier`, `SqlActionsCodeLensProvider`. Use a plain noun ("the schedule action", "the data-diff tool").
- **Framework internals** — `Rust state machine`, `TypeScript orchestrator`, `MetricFlow`, `inversify`, `Pydantic`, `Zod`. Drop.
- **Database-internal SQL syntax** — `TOP injection`, `sys.* catalog queries`, `DATETRUNC()`, `CONVERT(DATE, …, 23)`, `SELECT COUNT(*)`. Replace with "T-SQL support" or just drop.
- **Implementation mechanics** — "BFS traversal", "ConnectionPool", "cumulative SELECT", "max_completion_tokens normalization". Replace with what it produces ("full upstream/downstream traversal", "concurrent connections", "the parameter shape each model expects").
- **Internal lifecycle narratives** — "used to wait for an `isInstalled()` check before rendering… on the webview-ready handler". Say what's different now ("the panel opens instantly").
- **Auth flow enumerations** — listing all 7 Azure AD flows by name. Group ("service-principal, MSI, CLI").
- **Jira IDs** — `AI-XXXX` (CI validator rejects these anyway).
- **Slack URLs and `@username` mentions**.
- **`TODO`/`FIXME`/`XXX` markers**.

**Trim lightly:**
- Internal endpoint names that name the same thing in plain English — fine to mention once if the user might actually encounter them. Otherwise drop.
- Numbered metric DSL lists (`equals, startsWith, contains, in`, AND/OR composition) — usually verbose; say "your tenant's ownership rules" instead.
- Settings names — admin settings like `ssoUserRefreshMins` are defensible (admins set them), but consider plain English ("the SSO inactivity timeout setting") when the prose reads better that way.

**Keep:**
- Numbers that tell a story (250 min → 50 min; 11 foundation models; 22 built-in skills).
- The actual product or feature name as the user sees it.
- The scenario list that explains scope ("CASE branches, JOINs, GROUP BY, division-by-zero, incremental loads").
- Standard dbt or warehouse vocabulary that users already speak (`ref`, `source`, `config`, `profiles.yml`, `schema.yml`, dbt Cloud, dbt Power User).
- The single most concrete example ("`EDS_HUMAN_WH_LARGE`" makes the "we show warehouse names now" sentence land — keep one).

### When in doubt, split

If an entry bundles two unrelated wins under one title (e.g. "dbt syntax highlighting AND Detect Python from terminal"), split into two for discoverability. The reviewer feedback for April specifically called this out.

## Phase 6 — Validate

1. Run `python3 .github/scripts/validate.py` with `ENTRIES_DIR` pointed at `generated/<month>-2026/`. The easiest way: a small inline Python snippet that imports `validate.py` and overrides `ENTRIES_DIR`.
2. Fix any violations and re-run until "Validated N entries — all good."
3. Common failures and fixes:
   - **Title > 80 chars** — tighten or split.
   - **Backtick in `description`** — YAML can't parse a backtick at the start of a scalar; reword.
   - **Link host not in allowed_hosts** — drop the link or use a plain noun.
   - **Filename / date mismatch** — fix the filename to match the frontmatter date.

## Phase 7 — Commit

1. Update `.gitignore` to include `.github/meta/` if not already (local commit-message scratch).
2. `git add scripts/ generated/<month>-2026/ .gitignore`.
3. Write the commit message to `.github/meta/commit.txt` using HEREDOC, then `git commit -F .github/meta/commit.txt`. The message should:
   - Start with `feat: pipeline scripts + <Month> 2026 draft entries (N, flagged draft)`.
   - List the headline clusters as bullets.
   - End with `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`.
4. Do **NOT** push. Local-only.

## Phase 8 — Notion review page

1. Use the `mcp__claude_ai_Notion__notion-create-pages` tool.
2. Parent page ID: `31941b8929268119a3dbe8587a516284` (Product Change Logs).
3. Title: `Altimate Changelog — <Month> 2026 (Draft for Review)` (add `, Month-to-Date` if partial).
4. Icon: `📋`.
5. Content structure (match the existing April / March pages):
   - Header: product / period / tags row
   - "Purpose of this page" paragraph
   - Optional `> What changed in this revision:` blockquote (for re-revisions only)
   - Stats line — counts of new / improved / beta
   - `## 🆕 New Features` section listing all `tag: new` entries with body + source PRs + draft file path
   - `## ✅ Improvements` section listing all `tag: improved` entries
   - `## 🧪 Beta` section (if any)
   - `## Next steps` with reviewer instructions
6. Return the Notion URL to the user.

## Phase 9 — Summary

Print a final summary table:

```
<Month> 2026 — N entries (X new, Y improved, Z beta)

Branch: feat/<month>-2026-changelog-drafts (local, not pushed)
Validator: N/N passing
Notion: https://www.notion.so/<page-id>

Headlines:
  - <one line per major cluster>

Next:
  1. Team reviews Notion page
  2. Apply reviewer feedback to draft files
  3. When approved: move files to entries/, strip draft:true, open PR
```

## Voice for your responses

Direct, no "Certainly!" or "Great question!". Phase summaries are 1-3 sentences each. When asking for confirmation between phases, frame it as a yes/no with the key facts ("Fetched 240 releases, 1,800 PRs across 7 repos. Proceed to triage?").

## What you must never do

- **Push to remote.** This skill produces local branches only. Pushing is a separate human decision.
- **Promote files into `entries/` directly.** Always land them in `generated/<month>-2026/` first.
- **Drop `draft: true` from frontmatter** without explicit reviewer approval. Drafts must stay drafts until promoted.
- **Make up product slugs** — only the five in `products.yml`.
- **Skip the validator.** Even one CI failure on a 25-entry batch makes the whole PR fail.
- **Run end-to-end without checkpoints.** The fetch, triage, consolidation, and writing phases each need a human "yes" before continuing. Volume + irreversibility makes silent autonomy risky here.
- **Commit `data/`** — the raw release/PR data from private repos. The `.gitignore` covers this, but double-check.
- **Bundle two unrelated features into one entry** — reviewer feedback for April specifically flagged this.
