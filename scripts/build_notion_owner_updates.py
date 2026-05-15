#!/usr/bin/env python3
"""Build per-page content_updates JSON for adding Owners + 3 checkboxes to each
entry on the April / March / May Notion review pages.

Output (one file per month, suitable for piping to notion-update-page):
  /tmp/notion_owner_updates_<month>.json
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Author login → (display name, Notion user UUID with dashes).
# Resolved from `notion-get-users` against the AltimateAI workspace.
# Excluded: app/altimate-harness-bot (bot), VJ-yadav / sahrizvi / tsekityam
# (no Notion workspace match — external contributors).
LOGIN_TO_USER = {
    "Sourabhchrs93":        ("Sourabh Chourasia",   "1d6d872b-594c-8183-9084-000254ebed49"),
    "Bharatram-altimate-ai":("Bharatram Natarajan", "2a0d872b-594c-8176-9978-0002655178b6"),
    "aidtya":               ("Aditya Pandey",       "1f1d872b-594c-8169-99dc-0002835558a6"),
    "aloks98":              ("Alok Sahoo",          "1e3d872b-594c-8193-bfaa-00029e20981a"),
    "anandgupta42":         ("Anand Gupta",         "09e8b5de-5315-41cf-8375-f5ec3cd5f8f2"),
    "arora-saurabh448":     ("Saurabh Arora",       "1c5d872b-594c-8182-8f4d-0002919bd6a8"),
    "dev-punia-altimate":   ("Dev Punia",           "2bed872b-594c-8174-8ba8-0002603fbac9"),
    "dvanaken":             ("Dana Van Aken",       "18cd872b-594c-81d5-a8ce-0002db8ab50f"),
    "gaurpulkit":           ("Pulkit Gaur",         "665b0e74-cb2a-4535-b05c-787bf34449c8"),
    "hkaltai":              ("Harish Kumar",        "357d872b-594c-8172-801a-0002cb9980aa"),
    "ichandann":            ("Chandan Singha",      "2edd872b-594c-813c-b29d-0002c6658914"),
    "kulvirgit":            ("kulvir gahlawat",     "259d872b-594c-8124-9d4c-0002f9920682"),
    "mdesmet":              ("Michiel De Smet",     "6ca0d517-783b-4c60-a3d0-2a14336ce539"),
    "ralphstodomingo":      ("Ralph Sto. Domingo",  "2cbd872b-594c-8146-8cfb-0002d5d1bec1"),
    "sanjaykr5":            ("Sanjay Kumar",        "270d872b-594c-8171-8a5e-0002970855d3"),
    "saravmajestic":        ("Saravanan Shanmugam", "04a38539-f2c9-4c46-975b-07f67190f91a"),
    "shreyastelkar":        ("Shreyas Telkar",      "2bcd872b-594c-817f-b851-0002970e0074"),
    "suryaiyer95":          ("Surya Iyer",          "aad7c214-2886-491c-9c10-4a6814ba0bda"),
}

# PR_MAP duplicated from extract_owners.py — the source-PR lists used in each
# entry, needed to build the exact `**Source PRs:** ...` anchor string.
PR_MAP = {
    # April
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


def month_of(slug: str) -> str:
    # slug starts with YYYY-MM-DD
    return slug[:7]  # e.g. "2026-04"


def month_dir(slug: str) -> str:
    if slug.startswith("2026-04"):
        return "april-2026"
    if slug.startswith("2026-03"):
        return "march-2026"
    if slug.startswith("2026-05"):
        return "may-2026"
    raise ValueError(slug)


def build_source_prs_line(slug: str) -> str:
    refs = PR_MAP[slug]
    parts = [
        f"[{r}#{n}](https://github.com/AltimateAI/{r}/pull/{n})"
        for r, n in refs
    ]
    return "**Source PRs:** " + ", ".join(parts)


def build_owners_line(logins: list[str]) -> str:
    mentions = []
    externals = []
    for login in logins:
        if login in LOGIN_TO_USER:
            name, uid = LOGIN_TO_USER[login]
            mentions.append(
                f'<mention-user url="{{{{user://{uid}}}}}">{name}</mention-user>'
            )
        elif login.startswith("app/") or login.endswith("[bot]"):
            continue  # silently drop bots
        else:
            externals.append(login)
    parts = list(mentions)
    if externals:
        ext_str = ", ".join(f"`@{e}` (external)" for e in externals)
        parts.append(ext_str)
    if not parts:
        return "**Owners:** *_no internal owner — please assign_*"
    return "**Owners:** " + " ".join(parts)


CHECKBOXES = (
    "- [ ] is_owner_verified\n"
    "- [ ] is_sa_verified\n"
    "- [ ] is_product_verified"
)


def main() -> None:
    owners = json.loads((ROOT / "data" / "owners_by_entry.json").read_text())

    by_month: dict[str, list[dict]] = {"april": [], "march": [], "may": []}

    for slug, logins in owners.items():
        owners_line = build_owners_line(logins)
        source_prs_line = build_source_prs_line(slug)
        draft_line = f"**Draft file:** `generated/{month_dir(slug)}/{slug}.md`"

        old_str = f"{source_prs_line}\n{draft_line}"
        new_str = (
            f"{owners_line}\n\n"
            f"{source_prs_line}\n\n"
            f"{CHECKBOXES}\n\n"
            f"{draft_line}"
        )

        month = month_dir(slug).split("-")[0]
        by_month[month].append({"old_str": old_str, "new_str": new_str})

    for month, updates in by_month.items():
        out_path = Path(f"/tmp/notion_owner_updates_{month}.json")
        out_path.write_text(json.dumps(updates, indent=2) + "\n")
        print(f"{month}: {len(updates)} updates → {out_path}")


if __name__ == "__main__":
    main()
