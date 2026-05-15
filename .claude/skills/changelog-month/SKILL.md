---
name: changelog-month
description: Generate a changelog draft for a date window — month or week — by fetching releases across all 8 source repos, triaging features, consolidating clusters, writing polished entries with owner mentions and verification checkboxes, validating, committing to a branch, and creating a Notion review page. Use weekly (mid-cycle) or monthly (end of month) — same pipeline, different window. Invoke as `/changelog-month 2026-04` (monthly), `/changelog-month 2026-W19` (ISO week), `/changelog-month 2026-05-11..2026-05-17` (custom range), or `/changelog-month` and answer prompts.
---

# Changelog draft (monthly or weekly)

You are generating customer-facing changelog entries for the Altimate Platform across a date window. The output is a branch with polished draft entries, validated against the CI schema, plus a Notion review page for the team — with owner @-mentions and three verification checkboxes (`is_owner_verified`, `is_sa_verified`, `is_product_verified`) on every entry.

This skill supports two cadences:

- **Monthly** — full calendar month (e.g. `2026-04`). Window is `YYYY-MM-01..end-of-month`. Expect 15–25 polished entries.
- **Weekly** — ISO calendar week or a custom 7-ish-day range (e.g. `2026-W19` or `2026-05-11..2026-05-17`). Window is `start..end inclusive`. Expect 3–8 polished entries.

The pipeline (fetch → triage → consolidate → write → validate → commit → Notion) is identical for both — only the date window, directory/branch naming, and Notion page title change.

This skill is a **multi-phase recipe**. After each phase, summarize what happened and confirm with the user before moving on — do not run end-to-end in one go without checkpoints.

## Read first

Before phase 1, read in order:

1. `STYLE.md` — voice and tone rules.
2. `products.yml` — closed list of product slugs and `allowed_hosts`.
3. The most recent 3-5 files in `entries/` to ground the voice.
4. `scripts/build_features.py` — to understand the classifier and dedup logic the triage uses.
5. **The "Trim rules" section below** — reviewer-confirmed patterns to apply preemptively.

## Inputs

Look at the invocation. The user may have given you one of:

- **Month identifier** `YYYY-MM` (e.g. `2026-04`) → cadence = `monthly`.
- **ISO week** `YYYY-Www` (e.g. `2026-W19`, `2026-w19`) → cadence = `weekly`.
- **Custom range** `YYYY-MM-DD..YYYY-MM-DD` → cadence = `custom` (treat like weekly downstream).
- Nothing → ask: "Which window? (`YYYY-MM` for a month, `YYYY-Www` for an ISO week, or `YYYY-MM-DD..YYYY-MM-DD` for a custom range)"

**Resolve the date window:**
- Monthly: `WINDOW_START = YYYY-MM-01`, `WINDOW_END` = last day of month. For the current month (month-to-date), `WINDOW_END` = today's date.
- Weekly (ISO): Use Python's `datetime.fromisocalendar(year, week, 1)` for Monday, plus 6 days for Sunday. The skill is run AFTER the week closes, so default `WINDOW_END` = the Sunday. For the current ISO week (week-to-date), `WINDOW_END` = today's date.
- Custom range: take the dates as given.

**Resolve naming conventions** based on cadence — these are referenced throughout the remaining phases:

| Variable | Monthly | Weekly / Custom |
|---|---|---|
| `<WINDOW>` | `april-2026` (lowercase month name) | `2026-w19` or `2026-05-11_2026-05-17` |
| Generated dir | `generated/<WINDOW>/` | `generated/<WINDOW>/` |
| Branch name | `feat/<WINDOW>-changelog-drafts` | `feat/<WINDOW>-changelog-drafts` |
| Triage script | `scripts/<month>_triage.py` (e.g. `april_triage.py`) | `scripts/<WINDOW>_triage.py` |
| Notion title | `Altimate Changelog — <Month> 2026 (Draft for Review)` | `Altimate Changelog — Week of <YYYY-MM-DD> (Draft for Review)` |
| Notion title for partial month | `… (Draft for Review, Month-to-Date)` | `… (Draft for Review, Week-to-Date)` |

## Phase 1 — Setup

1. Run `git status --short`. If there are uncommitted changes that don't belong to this work, stop and ask the user what to do — never wipe their work.
2. Switch to `main` and pull (`git checkout main`). Branch off as `feat/<WINDOW>-changelog-drafts` (e.g. `feat/april-2026-changelog-drafts` for monthly, `feat/2026-w19-changelog-drafts` for weekly).
3. Check if `scripts/` and the `.gitignore` updates exist on `main`:
   - If they do: continue.
   - If they don't (typical — only on the per-window branches): restore them from the most recent existing window branch with `git checkout <prior-branch> -- scripts/ .gitignore`. If no prior window branch exists, ask the user to point at the branch that has the scripts.
4. Confirm the working tree has: `scripts/{fetch_releases,fetch_pr_bodies,build_features,build_curation,polish_entries,generate_entries,reparse_releases,extract_owners,build_notion_owner_updates}.py`.
5. Print a one-line summary and ask: "Branch ready. Proceed to fetch?"

## Phase 2 — Fetch releases + PR bodies

1. Run `scripts/fetch_releases.py --since <WINDOW_START> --out data/releases_<WINDOW>.json`. Note the per-repo release counts — if any repo returns 0 for a full window, flag it (might indicate a fetch regression).
   - **Sources in scope (8 repos):** `altimate-backend`, `altimate-frontend`, `vscode-dbt-power-user`, `altimate-code`, `altimate-core`, `altimate-mcp-engine`, `vscode-altimate-mcp-server`, `altimate-dbt-snowflake-query-tags`. The full list with primary-product mapping lives in `scripts/fetch_releases.py::REPOS`.
   - **`altimate-core` is a published library** (powers Altimate Code's SQL engine). Its release bodies are install/deploy artifacts, not PR lists. The fetcher uses the `REPOS_NEEDING_COMPARE_FALLBACK` set + GitHub compare API to enumerate PRs between consecutive tags from commit messages — same downstream shape, just sourced differently. Don't be surprised by low PR counts; altimate-core typically only sees a handful of feature PRs per release.
   - For **weekly** runs `--since` is a Monday or the explicit start date; the fetch script doesn't filter on an end date, so downstream triage will clip to `WINDOW_END`.
2. Run `scripts/fetch_pr_bodies.py --releases data/releases_<WINDOW>.json --out data/prs_<WINDOW>.json --workers 8`. Use `run_in_background` if expected total > 500 PRs — the GraphQL fetch is ~12 PRs/sec.
3. Print totals: releases per repo, total PRs.
4. Ask: "Fetched N releases / M PRs. Proceed to triage?"

## Phase 3 — Triage

1. Write or reuse a `scripts/<WINDOW>_triage.py` (clone of an existing triage script — `march_triage.py` / `may_triage.py` — with the date window updated). It must:
   - Filter `pr_release_idx` to the `WINDOW_START..WINDOW_END` inclusive.
   - Use `primary_product` from each repo (the new-repo classifier lookup) so dbt-power-user / altimate-code / datamates entries get product tags even when keywords don't match.
   - Apply `feat:` prefix + Jira dedup + paired-PR dedup + trivial filter from `build_features.py`.
   - Apply the SHIP/SKIP regex patterns documented at the bottom of the prior triage scripts.
   - Write `data/features_<WINDOW>.json`.
2. Run it. Print the triage table grouped by week (for monthly) or by day (for weekly). Highlight:
   - **SHIP** — clear customer-visible features. Monthly: ~15–30 typically. Weekly: ~3–8.
   - **REVIEW** — your call (~10–30 monthly / ~2–6 weekly; ambiguous, often the most interesting).
   - **SKIP** — internal infra, schema migrations, model routing, analytics tracking.
3. Ask the user to:
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

For each cluster, write a file at `generated/<WINDOW>/YYYY-MM-DD-<slug>.md`. The date is the **latest** ship date in the cluster.

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

1. Run `python3 .github/scripts/validate.py` with `ENTRIES_DIR` pointed at `generated/<WINDOW>/`. The easiest way: a small inline Python snippet that imports `validate.py` and overrides `ENTRIES_DIR`.
2. Fix any violations and re-run until "Validated N entries — all good."
3. Common failures and fixes:
   - **Title > 80 chars** — tighten or split.
   - **Backtick in `description`** — YAML can't parse a backtick at the start of a scalar; reword.
   - **Link host not in allowed_hosts** — drop the link or use a plain noun.
   - **Filename / date mismatch** — fix the filename to match the frontmatter date.

## Phase 7 — Commit

1. Update `.gitignore` to include `.github/meta/` if not already (local commit-message scratch).
2. `git add scripts/ generated/<WINDOW>/ .gitignore`.
3. Write the commit message to `.github/meta/commit.txt` using HEREDOC, then `git commit -F .github/meta/commit.txt`. The message should:
   - Start with `feat: pipeline scripts + <Month> 2026 draft entries (N, flagged draft)` (monthly) or `feat: pipeline scripts + week of <YYYY-MM-DD> draft entries (N, flagged draft)` (weekly).
   - List the headline clusters as bullets.
   - End with `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`.
4. Do **NOT** push. Local-only.

## Phase 8 — Notion review page

1. **Build the owner map.** Before assembling the page content, run
   `scripts/extract_owners.py` to produce `data/owners_by_entry.json` —
   `{slug: [github_login, ...]}` derived from the cached PR records. Each
   feature's PR list (the `PR_MAP` constant inside the script) determines its
   owners, so keep that map in lockstep with the entries written in Phase 5.

2. **Map GitHub logins → Notion user IDs.** The current mapping lives in
   `scripts/build_notion_owner_updates.py::LOGIN_TO_USER`. For each unique
   author that isn't already in the dict, look them up:
   - Use `notion-search` with `query_type="user"` and `query="<First Last>"`.
     The result contains the URL in the form `{{user://<dashed-uuid>}}` —
     that's the URL form `<mention-user>` requires.
   - Add a new entry to the dict: `"github-login": ("Display Name", "<dashed-uuid>")`.
   - **Excluded categories** (never @-mentioned):
     - **Bots**: logins matching `app/*` or ending with `[bot]`. Drop silently.
     - **External contributors**: GitHub authors with no Notion workspace user.
       Show as plain text `` `@<login>` (external) `` so the team can see they
       were involved, but no notification fires.

3. **Use the `mcp__claude_ai_Notion__notion-create-pages` tool.**
   - Parent page ID: `31941b8929268119a3dbe8587a516284` (Product Change Logs).
   - Title: `Altimate Changelog — <Month> 2026 (Draft for Review)` (add
     `, Month-to-Date` if partial).
   - Icon: `📋`.

4. **Page structure (match the existing April / March / May pages):**
   - Header: product / period / tags row.
   - `## Purpose of this page` paragraph.
   - Optional `> What changed in this revision:` blockquote (for re-revisions).
   - Stats line — counts of new / improved / beta.
   - `## 🆕 New Features` section.
   - `## ✅ Improvements` section.
   - `## 🧪 Beta` section (if any).
   - `## Roles & sign-off` section (see below — non-negotiable).
   - `## Next steps` section (see below — references the three checkboxes).

   **`## Roles & sign-off` section content (paste verbatim — this defines the verification model the checkboxes enforce):**

   ```
   ## Roles & sign-off

   Each entry needs **three sign-offs** before promotion. The **Owner** drives the process for their entries — gathering the SA review and Product review, applying any feedback, and ticking each checkbox once the corresponding sign-off is in.

   - **Owner** — verifies the description matches what shipped (correctness vs implementation). Owns the entry end-to-end through promotion.
   - **SA** — verifies the feature works as described; adds a screenshot or short Loom/YouTube video if the feature is UI-visible.
   - **Product** — reviews release-note quality through a marketing lens; flags anything that reads as engineering notes, lacks user benefit, or buries the headline.
   ```

   **`## Next steps` section content (substitute `<WINDOW>` and any month-specific lines):**

   ```
   ## Next steps

   1. **Owners**: review your entries (search this page for your @-mention). For each entry you own:
      - Confirm the description matches what shipped → tick `is_owner_verified`.
      - Loop in the SA on Slack with the entry link → they test, add media if needed, tick `is_sa_verified`.
      - Loop in Product with the entry link → they review for release-note quality, tick `is_product_verified`.
   2. **Apply feedback** to draft files on branch `feat/<WINDOW>-changelog-drafts` in the changelog repo. Notion comments on the section are the source of truth.
   3. (Weekly only) **End-of-week refresh**: if any PRs land late, re-run the pipeline for the same window and update this page in place.
   4. (Monthly partial-month only) **End-of-month refresh**: re-run the pipeline after the month closes to pick up remaining days, and update this page in place.
   5. **Promotion** (only when all three checkboxes are ticked on an entry): move that approved file from `generated/<WINDOW>/` → `entries/`, strip `draft: true`, open a PR against [AltimateAI/changelog](https://github.com/AltimateAI/changelog). Entries with mixed checkbox state stay in `generated/`.
   6. CI runs the schema validator (`.github/scripts/validate.py`) on every PR.
   ```

5. **Per-entry section format (this is non-negotiable — every entry must have
   the Owners line + 3 checkboxes from the first creation):**

   ```
   ### <emoji> <title>

   **Date:** YYYY-MM-DD  |  **Products:** `<comma-separated slugs>`  |  **Tag:** `<new|improved|beta>`

   <body paragraphs>

   **Owners:** <mention-user url="{{user://<uuid>}}">Display Name</mention-user> <mention-user url="{{user://<uuid>}}">Display Name</mention-user>

   **Source PRs:** [repo#N](https://github.com/AltimateAI/<repo>/pull/N), ...

   - [ ] is_owner_verified
   - [ ] is_sa_verified
   - [ ] is_product_verified

   **Draft file:** `generated/<WINDOW>/<slug>.md`

   ---
   ```

   **External-only entry variant** (no internal owner mapped):

   ```
   **Owners:** `@<github-login>` (external)
   ```

   **No-owner fallback** (rare — all authors excluded as bots/externals):

   ```
   **Owners:** *_no internal owner — please assign_*
   ```

6. **URL format gotcha (hard-won learning, do not deviate):** The
   `<mention-user>` URL **must** be `{{user://<dashed-uuid>}}` —
   Notion's compressed-URL form. Other URL forms that look reasonable will
   silently fail:
   - ❌ `https://www.notion.so/<undashed-uuid>` — strips to plain-text URL, no mention.
   - ❌ `https://www.notion.so/<dashed-uuid>` — same failure.
   - ❌ `https://www.notion.so/<workspace>/<uuid>` — same failure.
   - ✅ `{{user://<dashed-uuid>}}` — renders as @mention, fires notification.
   The compressed form is what `notion-search` with `query_type="user"`
   returns; copy that string into the URL attribute directly.

7. **Return the Notion URL to the user.**

8. **If you're updating an existing page** (re-revision or post-hoc fix), use
   `notion-update-page` with `command="update_content"` and
   `content_updates=[{old_str, new_str}, ...]`. Each anchor (`old_str`) needs
   to be unique on the page — typically the existing `Source PRs` line + the
   `Draft file` line is a safe unique pair. Match the stored form: pipes in
   `**Date:** ... | ...` are unescaped in your anchor (Notion's fetch shows
   them as `\|` but the storage form is `|`).

## Phase 9 — Summary

Print a final summary table:

```
<Month> 2026 — N entries (X new, Y improved, Z beta)
  (or)
Week of <YYYY-MM-DD> — N entries (X new, Y improved, Z beta)

Branch: feat/<WINDOW>-changelog-drafts (local, not pushed)
Validator: N/N passing
Owners: K entries with internal owners @-mentioned, J with external-only fallback
Notion: https://www.notion.so/<page-id>

Headlines:
  - <one line per major cluster>

Three-role sign-off model:
  - Owner — verifies correctness vs implementation; drives sign-offs for the entry end-to-end
  - SA — tests the feature; adds screenshot or Loom/YouTube video if UI-visible
  - Product — reviews release-note quality through a marketing lens

Next:
  1. Owners loop in SA and Product per entry; each role ticks its own checkbox
  2. Apply reviewer feedback to draft files
  3. When all 3 checkboxes are ticked on an entry: move that file to entries/, strip draft:true, open PR (entries promote per-row, not as a batch)
```

## Voice for your responses

Direct, no "Certainly!" or "Great question!". Phase summaries are 1-3 sentences each. When asking for confirmation between phases, frame it as a yes/no with the key facts ("Fetched 240 releases, 1,800 PRs across 7 repos. Proceed to triage?").

## What you must never do

- **Push to remote.** This skill produces local branches only. Pushing is a separate human decision.
- **Promote files into `entries/` directly.** Always land them in `generated/<WINDOW>/` first.
- **Drop `draft: true` from frontmatter** without explicit reviewer approval. Drafts must stay drafts until promoted.
- **Make up product slugs** — only the five in `products.yml`.
- **Skip the validator.** Even one CI failure on a 25-entry batch makes the whole PR fail.
- **Run end-to-end without checkpoints.** The fetch, triage, consolidation, and writing phases each need a human "yes" before continuing. Volume + irreversibility makes silent autonomy risky here.
- **Commit `data/`** — the raw release/PR data from private repos. The `.gitignore` covers this, but double-check.
- **Bundle two unrelated features into one entry** — reviewer feedback for April specifically flagged this.
