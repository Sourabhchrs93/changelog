#!/usr/bin/env python3
"""Group PRs into feature units for the changelog.

Reads:
  data/releases.json
  data/prs.json (produced by fetch_pr_bodies.py)

Writes:
  data/features.json  — one entry per feature group, deduped across repos
  data/features.md    — human-readable summary for review

Pipeline:
  1. For each PR: classify products, detect Jira ID + paired-PR refs
  2. Drop trivial PRs (chore/test/ci/docs/refactor/dependabot)
  3. Group PRs: by Jira ID, else by paired-PR ref, else singleton
  4. Attach release metadata (which tag(s) shipped each PR)
  5. Emit features.json sorted by latest ship date desc
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASES_PATH = ROOT / "data" / "releases.json"
PRS_PATH = ROOT / "data" / "prs.json"
FEATURES_JSON = ROOT / "data" / "features.json"
FEATURES_MD = ROOT / "data" / "features.md"

# ---------- classification ----------

PRODUCT_RULES = [
    # order matters: first match wins on title; body adds extras
    ("databricks-app", re.compile(
        r"(?i)\b(databricks|\bdbx\b|dbx[_\s\-]|/dbx/|\bdbr\b|"
        r"\bspark\b|\bphoton\b|auto[\s-]?tune|databricks_jobs|workspace_id|"
        r"unity[\s-]?catalog|all[\s-]?purpose[\s-]?cluster|job[\s-]?cluster|"
        r"sku[\s-]?cost|dbu\b|dbus\b)"
    )),
    ("snowflake-app", re.compile(
        r"(?i)\b(snowflake|snowflake_jobs|\bsnow\b|warehouse|"
        r"tableau|bi[\s_-]?dashboard|looker|powerbi|power[\s-]?bi|"
        r"query[\s_-]?usage|query[\s_-]?tag|query[\s_-]?routing|"
        r"sf[\s-]copilot|cortex|account[\s-]?usage)"
    )),
    ("dbt-power-user", re.compile(
        r"(?i)\b(dbt[\s_-]power[\s_-]user|dbt[\s-]?powe[r]?|\bdbt[\s_-]model|"
        r"dbt_model|dbt_cloud|dbt[\s-]cloud|dbt[\s-]docs|dbt[\s-]core|"
        r"dbt[\s-]project|dbt[\s-]profile|datapilot)"
    )),
    ("altimate-code", re.compile(
        r"(?i)\b(altimate[\s-]?code|vscode[\s-]?extension|code[\s-]?extension|"
        r"ide[\s-]?integration|cursor[\s-]?integration|vsx|vs[\s-]?code)"
    )),
    ("datamates", re.compile(
        r"(?i)\b(datamates|data[\s-]?mate|\blineage\b|\bcatalog\b|"
        r"column[\s-]?lineage|glossary|metadata[\s-]?explorer)"
    )),
]

# Studio is shared platform — mark it as cross-product for both major apps
STUDIO_RE = re.compile(
    r"(?i)\b(studio|knowledge[\s-]?engine|prompt[\s-]?library|"
    r"agent[\s-]?ops|subscription)"
)

# Reach for default product when nothing else hits. Many backend PRs touch
# shared infra; we'll mark these as "unclassified" so the curator can decide.
DEFAULT_PRODUCT = None

# ---------- trivial filter ----------

TRIVIAL_TITLE_PREFIXES = (
    "chore:", "test:", "tests:", "ci:", "docs:", "doc:", "build:", "perf:",
    "style:", "refactor:", "revert:",
)
TRIVIAL_TITLE_SUBSTRINGS = (
    "bump ", "dependabot", "[skip ci]", "merge branch",
    "release ", "release:",
)
TRIVIAL_AUTHORS = {
    "dependabot[bot]", "renovate[bot]", "github-actions[bot]",
    "altimate-harness-bot[bot]", "altimate-bot[bot]",
}
# Words/phrases that signal an internal-only PR (CI, tests, infra, observability,
# logs, regression suites, alembic, etc.) — drop these from the customer changelog.
INTERNAL_ONLY_RE = re.compile(
    r"(?i)\b("
    r"langfuse|observability|telemetry|metric[s]?[\s-]?endpoint|"
    r"sentry|datadog|signoz|logging|loguru|"
    r"alembic|migration[s]?\b|schema[\s-]?migration|"
    r"regression[\s-]?test|flaky|smoke[\s-]?test|integration[\s-]?test|"
    r"\bci\b|github[\s-]?action|workflow[\s-]?(file|yaml|yml)|"
    r"typescript[\s-]?error|typecheck|tsconfig|eslint|prettier|"
    r"dependabot|vanta|soc2|sast|snyk|"
    r"unit[\s-]?test|jest[\s-]?test|pytest|"
    r"backfill|ingestion[\s-]?pipeline|dbt[\s-]?build|"
    r"warehouse[\s-]?adapter|connection[\s-]?pool|"
    r"\bmcp[\s-]?(server|tool|engine)|claude[\s-]?code|"
    r"refactor|cleanup|dead[\s-]?code|unused[\s-]?import"
    r")\b"
)

# ---------- extraction ----------

JIRA_RE = re.compile(r"\b(AI-\d{2,5})\b")
PAIRED_PR_RE = re.compile(
    r"AltimateAI/(altimate-(?:backend|frontend))(?:#|/pull/)(\d+)"
)
CONVENTIONAL_PREFIX_RE = re.compile(
    r"^\s*(feat|fix|chore|test|ci|docs|build|perf|refactor|revert|style)"
    r"(?:\([^)]*\))?\s*:\s*",
    re.IGNORECASE,
)


def classify_products(title: str, body: str, labels: list[dict]) -> list[str]:
    text = f"{title}\n{body or ''}"
    products: list[str] = []
    for product, pat in PRODUCT_RULES:
        if pat.search(text):
            if product not in products:
                products.append(product)
    # Studio touches both major apps — assign cross-cutting if no specific app matched
    if STUDIO_RE.search(text):
        if not products:
            products = ["snowflake-app", "databricks-app"]
    # Label hints from GitHub
    label_names = " ".join((l.get("name") or "").lower() for l in (labels or []))
    if "databricks" in label_names and "databricks-app" not in products:
        products.append("databricks-app")
    if "snowflake" in label_names and "snowflake-app" not in products:
        products.append("snowflake-app")
    return products


def is_trivial(title: str, body: str, author: str) -> bool:
    t = (title or "").strip()
    tl = t.lower()
    if author in TRIVIAL_AUTHORS:
        return True
    for p in TRIVIAL_TITLE_PREFIXES:
        if tl.startswith(p):
            return True
    for s in TRIVIAL_TITLE_SUBSTRINGS:
        if s in tl:
            return True
    # Internal-only signal: title or body matches infra/CI/observability keywords
    # AND title doesn't contain a clear user-visible signal
    text = f"{title}\n{body or ''}"
    if INTERNAL_ONLY_RE.search(t):
        return True
    return False


def clean_title(title: str) -> str:
    t = CONVENTIONAL_PREFIX_RE.sub("", title or "").strip()
    # drop [AI-1234] / [AI-0000]
    t = re.sub(r"\[AI-\d{2,5}\]\s*", "", t)
    # drop trailing PR number
    t = re.sub(r"\s*\(#\d+\)\s*$", "", t)
    return t.strip()


def extract_jira_ids(title: str, body: str) -> list[str]:
    ids = set()
    for s in (title, body or ""):
        for m in JIRA_RE.findall(s or ""):
            if m.upper() != "AI-0000":
                ids.add(m.upper())
    return sorted(ids)


def extract_paired_prs(body: str) -> list[tuple[str, int]]:
    out = []
    for repo, num in PAIRED_PR_RE.findall(body or ""):
        out.append((repo, int(num)))
    return out


# ---------- pipeline ----------

def load_data():
    releases = json.loads(RELEASES_PATH.read_text())
    prs = json.loads(PRS_PATH.read_text())
    return releases, prs


def build_pr_index(releases) -> dict[tuple[str, int], dict]:
    """Map (short_repo, pr_number) -> {tag, published_at}."""
    idx = {}
    for short_name, info in releases["repos"].items():
        for r in info["releases"]:
            for pr in r["prs"]:
                key = (short_name, pr["number"])
                # Keep the EARLIEST release that shipped this PR (chronologically first)
                if key not in idx or r["published_at"] < idx[key]["published_at"]:
                    idx[key] = {
                        "tag": r["tag"],
                        "published_at": r["published_at"],
                    }
    return idx


def main() -> None:
    releases, prs = load_data()
    pr_release_idx = build_pr_index(releases)

    # Build enriched PR list
    pr_records = []
    for key, pr in prs.items():
        if pr.get("_error"):
            continue
        short_repo, number_s = key.split(":", 1)
        number = int(number_s)
        title = pr.get("title") or ""
        body = pr.get("body") or ""
        author_obj = pr.get("author") or {}
        author = author_obj.get("login") or ""
        labels = pr.get("labels") or []

        prefix_match = CONVENTIONAL_PREFIX_RE.match(title)
        prefix = (prefix_match.group(1).lower() if prefix_match else "").strip()

        rec = {
            "key": key,
            "repo": short_repo,
            "number": number,
            "url": pr.get("url"),
            "title_raw": title,
            "title": clean_title(title),
            "body": body,
            "author": author,
            "labels": [l.get("name") for l in labels],
            "merged_at": pr.get("mergedAt"),
            "prefix": prefix,  # feat / fix / chore / ...
            "products": classify_products(title, body, labels),
            "jira_ids": extract_jira_ids(title, body),
            "paired": extract_paired_prs(body),
            "trivial": is_trivial(title, body, author),
        }
        rec.update(pr_release_idx.get((short_repo, number), {}))
        pr_records.append(rec)

    # Sort by ship date desc (newest first)
    pr_records.sort(key=lambda r: r.get("published_at") or "", reverse=True)

    # --- Group into feature units ---
    # Union-find over PR keys
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

    # 1) Group by Jira ID
    jira_to_keys: dict[str, list[str]] = defaultdict(list)
    for r in pr_records:
        for jid in r["jira_ids"]:
            jira_to_keys[jid].append(r["key"])
    for keys in jira_to_keys.values():
        if len(keys) > 1:
            base = keys[0]
            for k in keys[1:]:
                union(base, k)

    # 2) Group by paired PR mention (e.g., body mentions altimate-frontend#1234)
    for r in pr_records:
        for repo_paired, num_paired in r["paired"]:
            other_key = f"{repo_paired}:{num_paired}"
            if other_key in by_key:
                union(r["key"], other_key)

    # Bucket by root
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in pr_records:
        root = find(r["key"])
        groups[root].append(r)

    # Build feature records
    features = []
    for root, members in groups.items():
        # Drop groups that are entirely trivial
        non_trivial = [m for m in members if not m["trivial"]]
        if not non_trivial:
            continue
        # Require at least one feat: PR — fixes are too noisy for a changelog
        has_feat = any(m["prefix"] == "feat" for m in non_trivial)
        if not has_feat:
            continue
        members.sort(key=lambda m: m.get("published_at") or "", reverse=True)
        latest = members[0]
        # Union products across all members
        prods: list[str] = []
        for m in members:
            for p in m["products"]:
                if p not in prods:
                    prods.append(p)
        # Union jira ids
        jiras: list[str] = []
        for m in members:
            for j in m["jira_ids"]:
                if j not in jiras:
                    jiras.append(j)
        # Pick representative title — prefer longest non-trivial cleaned title
        title_pick = max(
            (m["title"] for m in non_trivial if m["title"]),
            key=lambda t: len(t),
            default=latest["title"],
        )
        # Cross-repo flag
        repos_involved = sorted({m["repo"] for m in members})
        features.append({
            "id": root,
            "title": title_pick,
            "products": prods,
            "jira_ids": jiras,
            "latest_published_at": latest.get("published_at"),
            "latest_tag": latest.get("tag"),
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
                    "published_at": m.get("published_at"),
                    "tag": m.get("tag"),
                }
                for m in members
            ],
        })

    # Sort features by latest ship date desc
    features.sort(key=lambda f: f.get("latest_published_at") or "", reverse=True)

    FEATURES_JSON.parent.mkdir(parents=True, exist_ok=True)
    FEATURES_JSON.write_text(json.dumps({
        "feature_count": len(features),
        "total_pr_count": sum(f["pr_count"] for f in features),
        "trivial_pr_count": sum(f["trivial_pr_count"] for f in features),
        "features": features,
    }, indent=2) + "\n")

    # Human-readable summary
    lines = [
        f"# Feature plan — {len(features)} feature groups",
        "",
        f"_Generated from {sum(f['pr_count'] for f in features)} PRs "
        f"({sum(f['trivial_pr_count'] for f in features)} trivial, filtered)._",
        "",
    ]
    # Group features by month
    by_month: dict[str, list[dict]] = defaultdict(list)
    for f in features:
        m = (f.get("latest_published_at") or "0000-00")[:7]
        by_month[m].append(f)
    for month in sorted(by_month.keys(), reverse=True):
        lines.append(f"## {month}")
        lines.append("")
        for f in by_month[month]:
            prods = ", ".join(f["products"]) or "(unclassified)"
            jira = " ".join(f["jira_ids"]) if f["jira_ids"] else ""
            repos = "+".join(r.replace("altimate-", "") for r in f["repos"])
            lines.append(
                f"- **{f['title']}** "
                f"_(repos: {repos}, products: {prods}{', ' + jira if jira else ''}, "
                f"PRs: {f['pr_count']}, tag: {f['latest_tag']})_"
            )
        lines.append("")
    FEATURES_MD.write_text("\n".join(lines) + "\n")

    # Stats
    unclassified = sum(1 for f in features if not f["products"])
    cross_repo = sum(1 for f in features if len(f["repos"]) > 1)
    print(f"features: {len(features)}")
    print(f"  cross-repo (deduped): {cross_repo}")
    print(f"  unclassified: {unclassified}")
    print(f"  trivial PRs filtered: {sum(f['trivial_pr_count'] for f in features)}")
    by_prod = defaultdict(int)
    for f in features:
        for p in f["products"]:
            by_prod[p] += 1
        if not f["products"]:
            by_prod["(unclassified)"] += 1
    for p, n in sorted(by_prod.items(), key=lambda kv: -kv[1]):
        print(f"    {p}: {n}")
    print(f"\nWrote {FEATURES_JSON}")
    print(f"Wrote {FEATURES_MD}")


if __name__ == "__main__":
    main()
