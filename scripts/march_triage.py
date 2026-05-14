#!/usr/bin/env python3
"""One-off March 2026 triage from data/releases_march.json + data/prs_march.json.

Mirrors build_features.py logic but:
  - Reads from the March-specific data files (not data/releases.json).
  - Filters to 2026-03-01..2026-03-31 only.
  - Honors primary_product per repo from the releases payload.
  - Applies the same `feat:` filter, Jira dedup, and trivial filter as April.

Outputs:
  data/features_march.json — feature groups for March only.
  data/curation_march.md   — curation checklist (for completeness).
  stdout                   — SHIP / REVIEW / SKIP triage tables.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASES = json.loads((ROOT / "data" / "releases_march.json").read_text())
PRS = json.loads((ROOT / "data" / "prs_march.json").read_text())

# Import classifier/filter logic from build_features so we stay consistent
sys.path.insert(0, str(ROOT / "scripts"))
from build_features import (  # noqa: E402
    CONVENTIONAL_PREFIX_RE,
    classify_products,
    clean_title,
    extract_jira_ids,
    extract_paired_prs,
    is_trivial,
)

MARCH_START = "2026-03-01"
MARCH_END = "2026-03-31"


def build_pr_release_index(releases) -> dict[tuple[str, int], dict]:
    idx = {}
    for short, info in releases["repos"].items():
        for r in info["releases"]:
            if not (MARCH_START <= r["published_at"][:10] <= MARCH_END):
                continue
            for pr in r["prs"]:
                key = (short, pr["number"])
                if key not in idx or r["published_at"] < idx[key]["published_at"]:
                    idx[key] = {"tag": r["tag"], "published_at": r["published_at"]}
    return idx


def primary_product_for(short_repo: str) -> str | None:
    return RELEASES["repos"][short_repo].get("primary_product")


def main() -> None:
    pr_release_idx = build_pr_release_index(RELEASES)
    print(f"PRs shipped in releases dated 2026-03-*: {len(pr_release_idx)}")

    pr_records = []
    for (short, num), rel in pr_release_idx.items():
        key = f"{short}:{num}"
        pr = PRS.get(key)
        if not pr or pr.get("_error"):
            continue
        title = pr.get("title") or ""
        body = pr.get("body") or ""
        author_obj = pr.get("author") or {}
        author = author_obj.get("login") or ""
        labels = pr.get("labels") or []
        prefix_match = CONVENTIONAL_PREFIX_RE.match(title)
        prefix = (prefix_match.group(1).lower() if prefix_match else "").strip()

        # Classification — honor primary_product slug per repo, fall back to text-based
        products = classify_products(title, body, labels)
        prim = primary_product_for(short)
        if prim and prim not in products:
            products.insert(0, prim)

        rec = {
            "key": key,
            "repo": short,
            "number": num,
            "url": pr.get("url"),
            "title_raw": title,
            "title": clean_title(title),
            "body": body,
            "author": author,
            "labels": [l.get("name") for l in labels],
            "merged_at": pr.get("mergedAt"),
            "prefix": prefix,
            "products": products,
            "jira_ids": extract_jira_ids(title, body),
            "paired": extract_paired_prs(body),
            "trivial": is_trivial(title, body, author),
            "tag": rel["tag"],
            "published_at": rel["published_at"],
        }
        pr_records.append(rec)

    pr_records.sort(key=lambda r: r["published_at"], reverse=True)

    # Group by Jira ID + paired-PR refs
    parent: dict[str, str] = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    by_key = {r["key"]: r for r in pr_records}

    jira_to_keys: dict[str, list[str]] = defaultdict(list)
    for r in pr_records:
        for jid in r["jira_ids"]:
            jira_to_keys[jid].append(r["key"])
    for keys in jira_to_keys.values():
        if len(keys) > 1:
            base = keys[0]
            for k in keys[1:]:
                union(base, k)

    for r in pr_records:
        for repo_paired, num_paired in r["paired"]:
            other_key = f"{repo_paired}:{num_paired}"
            if other_key in by_key:
                union(r["key"], other_key)

    groups: dict[str, list[dict]] = defaultdict(list)
    for r in pr_records:
        root = find(r["key"])
        groups[root].append(r)

    features = []
    for root, members in groups.items():
        non_trivial = [m for m in members if not m["trivial"]]
        if not non_trivial:
            continue
        has_feat = any(m["prefix"] == "feat" for m in non_trivial)
        if not has_feat:
            continue
        members.sort(key=lambda m: m["published_at"], reverse=True)
        latest = members[0]
        prods: list[str] = []
        for m in members:
            for p in m["products"]:
                if p not in prods:
                    prods.append(p)
        jiras: list[str] = []
        for m in members:
            for j in m["jira_ids"]:
                if j not in jiras:
                    jiras.append(j)
        title_pick = max(
            (m["title"] for m in non_trivial if m["title"]),
            key=lambda t: len(t),
            default=latest["title"],
        )
        repos_involved = sorted({m["repo"] for m in members})
        features.append({
            "id": root,
            "title": title_pick,
            "products": prods,
            "jira_ids": jiras,
            "latest_published_at": latest["published_at"],
            "latest_tag": latest["tag"],
            "repos": repos_involved,
            "pr_count": len(members),
            "trivial_pr_count": sum(1 for m in members if m["trivial"]),
            "prs": [
                {
                    "repo": m["repo"],
                    "number": m["number"],
                    "title": m["title"],
                    "title_raw": m["title_raw"],
                    "author": m["author"],
                    "products": m["products"],
                    "url": m["url"],
                    "trivial": m["trivial"],
                    "published_at": m["published_at"],
                    "tag": m["tag"],
                }
                for m in members
            ],
        })

    features.sort(key=lambda f: f["latest_published_at"], reverse=True)

    (ROOT / "data" / "features_march.json").write_text(json.dumps({
        "feature_count": len(features),
        "features": features,
    }, indent=2) + "\n")

    print(f"\nMarch feature groups (feat: + dedup): {len(features)}")

    # Triage using same patterns as April
    NOISE_PATTERNS = [
        (r"posthog", "analytics instrumentation"),
        (r"^include \w+ in \w+ flag", "tenant flag config"),
        (r"^add \w+tenant ", "tenant config"),
        (r"^enable spark analysis for \w+ tenant", "tenant flag"),
        (r"dev-?workflow|harness sandbox", "internal dev tooling"),
        (r"apply worker|worker pod|read-side merge", "backend infra"),
        (r"auto[\s-]?recommendation table|configuration table", "schema migration"),
        (r"soft-?delete column|unique constraint|alembic|migration", "schema migration"),
        (r"shadow inference|learning-?model", "ML infra"),
        (r"add \w+ to DataStore|add attributes field", "schema"),
        (r"route LLM gateway|GPT-5|Anthropic fallback", "model routing"),
        (r"migrate.*to ClickHouse|migrate.*reads", "storage migration"),
        (r"add ClickHouse tables", "schema"),
        (r"\[task-cost\]|\[US-\d+\]", "internal tag"),
        (r"^expose.*API$|forward.*to.*queries|endpoints?\b.*\(\d/\d\)", "backend plumbing"),
        (r"paginated.*endpoint|/filters/\w+ endpoint", "backend plumbing"),
        (r"^rewire |^rebuild .*without |coalesced apply|gated|stacked on", "internal refactor"),
        (r"Discover summary aggregations|response accuracy", "internal"),
        (r"job tasks-tab", "backend pagination tweak"),
        (r"\[AI-\d+/\d+/\d+\]", "multi-jira backend bundle"),
        (r"auto-resize|cluster_automatic_history", "internal"),
        (r"widen.*constraint", "schema"),
        (r"^route ", "backend routing"),
        (r"align soft-delete", "schema"),
        (r"unit test|integration test|smoke test|flaky", "test"),
        (r"^add \w+ field to|^add \w+ column to", "schema"),
        (r"^add \w+ endpoint(s)?$", "API plumbing"),
        (r"helpers? \(\d/\d\)|REST wrappers?", "backend plumbing"),
        (r"^create dbx|^create \w+ table", "schema"),
        (r"gate \w+ routes by tenant", "rollout/feature flag"),
        (r"^add Databricks routes to Studio context map", "internal config"),
    ]
    SHIP_PATTERNS = [
        r"redesign ", r"\bnew \w+ page\b", r"add .* page",
        r"page layout",
        r"^add .* button", r"breadcrumb", r"column filter",
        r"Share to Slack", r"Schedule .* button",
        r"rollback note", r"View all schedules",
        r"restore search bar", r"instance filter",
        r"convert .* filters to API-backed",
        r"archive/delete", r"lazy session intent",
        r"attach report PDF", r"show warehouse name instead of id",
        r"custom date range selection",
        r"add Spark analysis pages", r"add Databricks Users page",
        r"add Databricks Jobs page", r"add Databricks AI/ML pages",
        r"add Databricks summary", r"add Databricks sidebar",
        r"include cost in single-job", r"Auto Tune UI feedback",
        r"Auto Tune tab",
        r"previous_day_same_weekday",
        r"expand Studio data coverage",
        r"min/max savings range",
        r"team attribution rules",
        r"truncate schedule name",
        r"referral signup",
        r"enable PostHog autocapture",
        r"ssoUserRefreshMins",
        r"cortex functions usage",
        r"Databricks Job Details",
        r"redesigned? Studio",
        r"show user names instead of principal",
        r"email notifications for QTP",
        r"dbt job level enhancements",
        # Common March surfaces
        r"insightsection|insight section",
        r"streamable[ -]?http",
        r"knowledge engine|knowledge hub",
        r"databricks observability",
        r"databricks .* support",
        r"workload analytics",
        r"custom tag filter",
        r"week.*aggregation|weekly aggregation",
        r"cost attribution",
        r"multi-?connection",
        r"smoother streaming|auto[-\s]?resiz",
        r"InsightSection",
        r"export .* lineage",
        r"sku cost",
        r"\bcortex\b",
    ]
    SHIP_RE = re.compile("|".join(SHIP_PATTERNS), re.IGNORECASE)

    def classify(f):
        t = f["title"]
        for pat, label in NOISE_PATTERNS:
            if re.search(pat, t, re.IGNORECASE):
                return "SKIP", label
        if SHIP_RE.search(t):
            return "SHIP", ""
        return "REVIEW", ""

    ship, skip, review = [], [], []
    for f in features:
        c, reason = classify(f)
        (ship if c == "SHIP" else skip if c == "SKIP" else review).append((f, reason))

    print(f"\n=== MARCH TRIAGE: {len(features)} features ===")
    print(f"  SHIP  : {len(ship)}")
    print(f"  REVIEW: {len(review)}")
    print(f"  SKIP  : {len(skip)}")

    def fmt(f):
        prods = ",".join(p.replace("-app", "").replace("-power-user", "-pu") for p in f["products"]) or "?"
        repos = "+".join(r.replace("altimate-", "")[:2] for r in f["repos"])
        cross = "+" if len(f["repos"]) > 1 else " "
        return f"  {cross}{f['latest_published_at'][:10]} [{repos:<5}|{prods:<28}] {f['title'][:80]}"

    def show(label, items, show_reason=False):
        print(f"\n## {label} ({len(items)})")
        items.sort(key=lambda x: x[0]["latest_published_at"], reverse=True)
        for f, reason in items:
            suffix = f"  ← {reason}" if show_reason and reason else ""
            print(fmt(f) + suffix)

    show("SHIP — promote to entries/", ship)
    show("REVIEW — your call", review)
    show("SKIP — internal / not customer-facing", skip, show_reason=True)


if __name__ == "__main__":
    main()
