#!/usr/bin/env python3
"""Generate `data/curation.md` — a checklist for picking which features get entries.

For each feature group from data/features.json, emit:
    - [ ] **Title** _(date, repos, PRs, Jira, link)_

Strong candidates are pre-marked `[x]`:
  - cross-repo (backend + frontend = paired customer-facing feature)
  - has a Jira ID (tracked work, usually substantive)
  - has 3+ PRs (substantial multi-PR effort)

Grouped by product → month (newest first). Unclassified features are last.

Usage:
    python scripts/build_curation.py

Workflow:
    1. Run this script → review data/curation.md
    2. Edit data/curation.md: toggle `[x]`/`[ ]` to choose what gets an entry
    3. Run scripts/polish_entries.py → drafts land in generated/
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEATURES_PATH = ROOT / "data" / "features.json"
OUT_PATH = ROOT / "data" / "curation.md"

PRODUCT_ORDER = [
    "snowflake-app",
    "databricks-app",
    "dbt-power-user",
    "datamates",
    "altimate-code",
]


def is_strong_candidate(feat: dict) -> bool:
    if len(feat["repos"]) > 1:
        return True
    if feat["jira_ids"]:
        return True
    if feat["pr_count"] >= 3:
        return True
    return False


def feature_line(feat: dict) -> str:
    marker = "[x]" if is_strong_candidate(feat) else "[ ]"
    date = (feat.get("latest_published_at") or "")[:10]
    repos = "+".join(r.replace("altimate-", "")[:2] for r in feat["repos"])
    jira = " ".join(feat["jira_ids"]) if feat["jira_ids"] else ""
    pr_links = ", ".join(
        f"[{p['repo'].replace('altimate-', '')}#{p['number']}]({p['url']})"
        for p in feat["prs"][:3]
    )
    extra = f", {jira}" if jira else ""
    fid = feat["id"]
    title = feat["title"].strip()
    return (
        f"- {marker} `{fid}` **{title}** "
        f"_(date: {date}, repos: {repos}{extra}, PRs: {feat['pr_count']}, "
        f"src: {pr_links})_"
    )


def main() -> None:
    data = json.loads(FEATURES_PATH.read_text())
    features = data["features"]

    by_product: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    unclassified_by_month: dict[str, list[dict]] = defaultdict(list)

    for f in features:
        month = (f.get("latest_published_at") or "0000-00")[:7]
        if not f["products"]:
            unclassified_by_month[month].append(f)
            continue
        # Place feature under EACH of its products (so a cross-cutting feature
        # appears in both sections — curator marks it once in whichever section
        # makes most sense; duplicate marks are deduped at polish time).
        for product in f["products"]:
            by_product[product][month].append(f)

    lines: list[str] = []
    lines.append("# Changelog curation")
    lines.append("")
    lines.append(
        f"_{len(features)} feature groups from {data['total_pr_count']} PRs "
        f"(filtered: feat: prefix only, internal/CI/test removed)._"
    )
    lines.append("")
    lines.append("## How to use")
    lines.append("")
    lines.append(
        "1. Toggle `[x]` next to features you want as customer changelog entries.\n"
        "2. Strong candidates (cross-repo, Jira-tracked, or multi-PR) are pre-marked.\n"
        "3. Run `python scripts/polish_entries.py` to emit polished drafts to `generated/`.\n"
        "4. The same feature appearing under multiple products is deduped by id — mark once."
    )
    lines.append("")
    lines.append(f"**Pre-marked strong candidates: "
                 f"{sum(1 for f in features if is_strong_candidate(f))} / {len(features)}**")
    lines.append("")
    lines.append("---")
    lines.append("")

    for product in PRODUCT_ORDER:
        months = by_product.get(product, {})
        if not months:
            continue
        total = sum(len(v) for v in months.values())
        lines.append(f"## {product} ({total})")
        lines.append("")
        for month in sorted(months.keys(), reverse=True):
            lines.append(f"### {month}")
            lines.append("")
            for feat in months[month]:
                lines.append(feature_line(feat))
            lines.append("")

    if unclassified_by_month:
        total = sum(len(v) for v in unclassified_by_month.values())
        lines.append(f"## unclassified ({total})")
        lines.append("")
        lines.append(
            "_These didn't match any product keyword. Mostly internal infra "
            "(LLM gateway, PostHog tracking, dev tooling) — but skim for missed "
            "customer features._"
        )
        lines.append("")
        for month in sorted(unclassified_by_month.keys(), reverse=True):
            lines.append(f"### {month}")
            lines.append("")
            for feat in unclassified_by_month[month]:
                lines.append(feature_line(feat))
            lines.append("")

    OUT_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT_PATH}")
    print(f"  total features: {len(features)}")
    print(
        f"  pre-marked: "
        f"{sum(1 for f in features if is_strong_candidate(f))}"
    )


if __name__ == "__main__":
    main()
