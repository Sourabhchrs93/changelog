#!/usr/bin/env python3
"""Extract {entry_slug → [author_login, ...]} for each month's entries.

Reads:
  generated/<month>-2026/*.md           (entry slugs)
  data/prs.json + data/prs_april_extras.json + data/prs_march.json + data/prs_may.json
                                         (PR author logins)
  data/features.json + data/features_march.json + data/features_may.json
                                         (PR → feature group mapping)

A hardcoded PR_MAP per entry mirrors what the assemble-Notion scripts already
use (the polished entries don't store source PRs in their frontmatter — the map
lives in the Notion-page-assembly scripts).

Writes:
  data/owners_by_entry.json — {slug: [author_login, ...]}
"""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PR_MAP = {
    # April (matches the Notion-assembly script)
    "2026-04-01-dbt-1-11-udf-lineage-in-mcp": [("altimate-mcp-engine", 179)],
    "2026-04-02-dbt-cloud-sync-consolidated": [("altimate-backend", 4203)],
    "2026-04-02-llm-guard-prompt-injection": [("altimate-backend", 4768)],
    "2026-04-02-remote-mcp-http-sse-transports": [("altimate-frontend", 2463)],
    "2026-04-04-altimate-code-gitlab-mr-review": [("altimate-code", 622)],
    "2026-04-04-altimate-code-login-and-project-profiles": [("altimate-code", 606), ("altimate-code", 605)],
    "2026-04-06-dbt-cloud-environment-aliases": [("altimate-backend", 4828)],
    "2026-04-06-studio-citations-sharing-scheduled-reports": [("altimate-frontend", 2366), ("altimate-backend", 3636)],
    "2026-04-06-table-level-lineage-csv-export": [("altimate-frontend", 2471), ("altimate-backend", 4823)],
    "2026-04-07-dbt-jinja-syntax-highlighting": [("vscode-dbt-power-user", 1866)],
    "2026-04-07-detect-python-from-terminal": [("vscode-dbt-power-user", 1870)],
    "2026-04-09-tokens-tab-and-deposit-flow": [("altimate-frontend", 2433)],
    "2026-04-11-datamates-chat-panel-polish": [("vscode-altimate-mcp-server", 294), ("vscode-altimate-mcp-server", 295), ("vscode-altimate-mcp-server", 299)],
    "2026-04-13-altimate-code-dbt-unit-test-generation": [("altimate-code", 674)],
    "2026-04-14-auto-suspend-savings-range": [("altimate-backend", 4897)],
    "2026-04-14-subscriptions-webhooks-cloning-team-alerts": [("altimate-backend", 4804), ("altimate-backend", 4659), ("altimate-backend", 4812), ("altimate-backend", 4815), ("altimate-backend", 4891), ("altimate-backend", 4873), ("altimate-frontend", 2526), ("altimate-frontend", 2485)],
    "2026-04-14-team-attribution-in-qtp-slack": [("altimate-backend", 4851)],
    "2026-04-15-cortex-ai-services-and-warehouse-names": [("altimate-frontend", 2539), ("altimate-frontend", 2508), ("altimate-backend", 4953), ("altimate-backend", 4923), ("altimate-backend", 4853)],
    "2026-04-15-cte-profiler-in-dbt-power-user": [("vscode-dbt-power-user", 1863)],
    "2026-04-15-schedule-name-validation-and-send-now": [("altimate-frontend", 2536)],
    "2026-04-15-schema-yaml-hovers-and-codelenses": [("vscode-dbt-power-user", 1872)],
    "2026-04-21-data-parity-skill-mssql-fabric-clickhouse": [("altimate-code", 705), ("altimate-code", 493)],
    "2026-04-21-databricks-ai-gateway-as-llm-provider": [("altimate-code", 649)],
    "2026-04-21-referral-program": [("altimate-frontend", 2545), ("altimate-backend", 4966)],
    "2026-04-22-databricks-jobs-spark-users-deep-dive": [("altimate-frontend", 2543), ("altimate-frontend", 2542), ("altimate-frontend", 2318), ("altimate-frontend", 2322), ("altimate-frontend", 2154)],
    "2026-04-22-datamate-skills-push-to-cursor-copilot-cline": [("vscode-altimate-mcp-server", 283), ("vscode-altimate-mcp-server", 288), ("altimate-mcp-engine", 182)],
    "2026-04-22-sso-inactivity-timeout": [("altimate-frontend", 2457), ("altimate-backend", 4734)],
    "2026-04-23-altimate-code-chat-in-dbt-power-user": [("vscode-dbt-power-user", 1864), ("vscode-dbt-power-user", 1906)],
    "2026-04-23-risingwave-adapter-support": [("vscode-dbt-power-user", 1889)],
    "2026-04-28-share-studio-to-slack-via-webhook": [("altimate-frontend", 2540), ("altimate-backend", 4961)],
    "2026-04-29-custom-date-range-on-workloads": [("altimate-frontend", 2578)],
    # March
    "2026-03-02-studio-transparency-v2": [("altimate-backend", 3729)],
    "2026-03-02-workloads-custom-tag-filters": [("altimate-frontend", 2272)],
    "2026-03-05-databricks-sql-warehouses-page": [("altimate-frontend", 2143)],
    "2026-03-09-daily-cost-alert-redesigned": [("altimate-backend", 4178)],
    "2026-03-11-playground-renamed-to-studio": [("altimate-frontend", 2343)],
    "2026-03-13-dbt-1-11-udf-lineage": [("vscode-dbt-power-user", 1833)],
    "2026-03-17-new-cortex-usage-history": [("altimate-backend", 3978)],
    "2026-03-18-alerts-searchable-tags-and-schedule": [("altimate-backend", 4357), ("altimate-frontend", 2295)],
    "2026-03-19-altimate-code-cli-commands": [("altimate-code", 30), ("altimate-code", 89), ("altimate-code", 235), ("altimate-code", 453)],
    "2026-03-19-altimate-code-skills-subsystem": [("altimate-code", 279), ("altimate-code", 148), ("altimate-code", 144), ("altimate-code", 170), ("altimate-code", 342)],
    "2026-03-19-altimate-code-three-modes": [("altimate-code", 282)],
    "2026-03-20-altimate-code-tui-polish": [("altimate-code", 281), ("altimate-code", 175), ("altimate-code", 38)],
    "2026-03-21-altimate-code-mcp-auto-discovery": [("altimate-code", 311)],
    "2026-03-22-altimate-code-new-llm-providers": [("altimate-code", 349), ("altimate-code", 340), ("altimate-code", 18)],
    "2026-03-24-altimate-code-chat-panel-gui": [("vscode-altimate-mcp-server", 284)],
    "2026-03-24-dbt-power-user-clear-run-history": [("vscode-dbt-power-user", 1837)],
    "2026-03-27-qtp-slack-improvements": [("altimate-backend", 4615), ("altimate-backend", 4643), ("altimate-backend", 4404)],
    "2026-03-30-altimate-code-clickhouse-mongodb-drivers": [("altimate-code", 574), ("altimate-code", 482)],
    "2026-03-30-calendar-scheduling-ungated": [("altimate-backend", 4434)],
    "2026-03-30-cortex-code-cli-usage-tracking": [("altimate-backend", 4715)],
    "2026-03-30-hierarchical-integration-filters-dbt-workloads": [("altimate-backend", 4498)],
    "2026-03-31-studio-full-thread-export": [("altimate-backend", 4641)],
    # May
    "2026-05-04-altimate-code-v0-7-upstream-bridge": [("altimate-code", 757)],
    "2026-05-05-subscription-test-notifications": [("altimate-frontend", 2583)],
    "2026-05-06-ai-services-instance-filter": [("altimate-frontend", 2590)],
    "2026-05-06-databricks-jobs-page-refresh": [("altimate-frontend", 2602), ("altimate-frontend", 2231), ("altimate-frontend", 2571)],
    "2026-05-08-altimate-code-chat-improvements": [("vscode-altimate-mcp-server", 312), ("vscode-dbt-power-user", 1908), ("vscode-altimate-mcp-server", 315), ("vscode-altimate-mcp-server", 314)],
    "2026-05-08-azure-databricks-connect-form": [("altimate-backend", 5144), ("altimate-frontend", 2617)],
    "2026-05-08-dbt-models-integration-environment-cascade": [("altimate-frontend", 2573)],
    "2026-05-10-qtp-email-notifications": [("altimate-backend", 5051)],
    "2026-05-11-dbt-power-user-local-lineage-and-search": [("vscode-dbt-power-user", 1933), ("altimate-frontend", 2638)],
    "2026-05-11-studio-reports-and-sessions": [("altimate-frontend", 2589), ("altimate-backend", 5090), ("altimate-backend", 5086), ("altimate-frontend", 2584), ("altimate-backend", 5052), ("altimate-backend", 5053)],
    "2026-05-12-databricks-clusters-workspace-filter": [("altimate-frontend", 2612)],
    "2026-05-14-databricks-auto-tune-in-the-ui": [("altimate-frontend", 2565), ("altimate-frontend", 2657), ("altimate-frontend", 2616)],
    "2026-05-14-databricks-subscription-alerts": [("altimate-frontend", 2616)],
    "2026-05-14-sku-cost-page-redesign": [("altimate-backend", 5178), ("altimate-frontend", 2642)],
}


def load_pr_caches() -> dict:
    """Merge all PR-body caches into one dict keyed by 'repo:number'."""
    cache = {}
    for fname in ("prs.json", "prs_april_extras.json", "prs_march.json", "prs_may.json"):
        path = ROOT / "data" / fname
        if not path.exists():
            continue
        cache.update(json.loads(path.read_text()))
    return cache


def author_for(pr_record: dict) -> str | None:
    if not pr_record or pr_record.get("_error"):
        return None
    a = pr_record.get("author") or {}
    return a.get("login")


def main() -> None:
    prs = load_pr_caches()
    owners_by_entry: dict[str, list[str]] = OrderedDict()
    missing: list[tuple[str, str, int]] = []

    for slug, pr_refs in PR_MAP.items():
        seen = []
        for repo, num in pr_refs:
            key = f"{repo}:{num}"
            rec = prs.get(key)
            login = author_for(rec)
            if not login:
                missing.append((slug, repo, num))
                continue
            if login not in seen:
                seen.append(login)
        owners_by_entry[slug] = seen

    out_path = ROOT / "data" / "owners_by_entry.json"
    out_path.write_text(json.dumps(owners_by_entry, indent=2) + "\n")

    # Unique authors across everything
    unique_authors = sorted({a for v in owners_by_entry.values() for a in v})
    print(f"Entries with owners: {len(owners_by_entry)}")
    print(f"Unique authors: {len(unique_authors)}")
    print(f"\nAuthors:")
    for a in unique_authors:
        print(f"  - {a}")
    if missing:
        print(f"\nMissing PR records ({len(missing)}):")
        for s, r, n in missing[:20]:
            print(f"  {s}: {r}#{n}")


if __name__ == "__main__":
    main()
