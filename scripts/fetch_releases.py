#!/usr/bin/env python3
"""Fetch GitHub releases from altimate-backend and altimate-frontend.

Usage:
    python scripts/fetch_releases.py [--since YYYY-MM-DD] [--out data/releases.json]

Requires `gh` CLI authenticated with access to AltimateAI org.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPOS = [
    # (short_name, repo_full_name, primary_product_slug_or_None)
    ("altimate-backend", "AltimateAI/altimate-backend", None),
    ("altimate-frontend", "AltimateAI/altimate-frontend", None),
    ("vscode-dbt-power-user", "AltimateAI/vscode-dbt-power-user", "dbt-power-user"),
    ("altimate-code", "AltimateAI/altimate-code", "altimate-code"),
    ("altimate-mcp-engine", "AltimateAI/altimate-mcp-engine", "datamates"),
    ("vscode-altimate-mcp-server", "AltimateAI/vscode-altimate-mcp-server", "datamates"),
    ("altimate-dbt-snowflake-query-tags",
     "AltimateAI/altimate-dbt-snowflake-query-tags", "datamates"),
]

PR_REF_RE = re.compile(r"https://github\.com/AltimateAI/[\w-]+/pull/(\d+)")
# Format A (autogen): "* title by @author in https://github.com/.../pull/123"
PR_LINE_A_RE = re.compile(
    r"^\*\s+(?P<title>.*?)\s+by\s+@(?P<author>[\w\-\[\]]+)\s+in\s+"
    r"https://github\.com/AltimateAI/[\w-]+/pull/(?P<num>\d+)\s*$"
)
# Format B (git-cliff style): "- [sha ]?title (#123) [(sha)]?"
PR_LINE_B_RE = re.compile(
    r"^-\s+(?:[0-9a-f]{7,40}\s+)?(?P<title>.+?)\s+\(#(?P<num>\d+)\)"
    r"(?:\s+\([0-9a-f]{7,40}\))?\s*$"
)


def run_gh(args: list[str], repo: str) -> str:
    cmd = ["gh", *args, "--repo", repo]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        sys.stderr.write(f"gh failed: {' '.join(cmd)}\n{result.stderr}\n")
        sys.exit(1)
    return result.stdout


def list_releases(repo: str, since: datetime) -> list[dict]:
    raw = run_gh(
        [
            "release", "list",
            "--limit", "500",
            "--json", "tagName,name,publishedAt,isPrerelease,isDraft",
        ],
        repo,
    )
    items = json.loads(raw)
    out = []
    for r in items:
        published = datetime.fromisoformat(r["publishedAt"].replace("Z", "+00:00"))
        if published < since:
            continue
        out.append(r)
    return out


def fetch_release_body(repo: str, tag: str) -> str:
    raw = run_gh(
        ["release", "view", tag, "--json", "body"],
        repo,
    )
    return json.loads(raw).get("body", "") or ""


def parse_prs(body: str) -> list[dict]:
    prs = []
    seen = set()
    for line in body.splitlines():
        s = line.strip()
        m = PR_LINE_A_RE.match(s)
        if m:
            num = int(m.group("num"))
            if num in seen:
                continue
            seen.add(num)
            prs.append({
                "number": num,
                "title": m.group("title").strip(),
                "author": m.group("author"),
            })
            continue
        m = PR_LINE_B_RE.match(s)
        if m:
            num = int(m.group("num"))
            if num in seen:
                continue
            seen.add(num)
            prs.append({
                "number": num,
                "title": m.group("title").strip(),
                "author": None,
            })
    return prs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--since",
        default=(datetime.now(timezone.utc) - timedelta(days=183)).date().isoformat(),
        help="ISO date; releases published on or after this date are included (default: ~6 months ago).",
    )
    parser.add_argument(
        "--out",
        default="data/releases.json",
        help="Output path relative to repo root.",
    )
    parser.add_argument(
        "--include-freemium",
        action="store_true",
        help="Include `freemium-*` tags from the frontend repo (excluded by default).",
    )
    args = parser.parse_args()

    since = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)
    repo_root = Path(__file__).resolve().parent.parent
    out_path = repo_root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "since": since.date().isoformat(),
        "include_freemium": args.include_freemium,
        "repos": {},
    }

    for short_name, repo, primary_product in REPOS:
        sys.stderr.write(f"Listing releases for {repo}...\n")
        releases = list_releases(repo, since)
        sys.stderr.write(f"  {len(releases)} releases since {since.date()}\n")

        enriched = []
        for r in releases:
            tag = r["tagName"]
            if not args.include_freemium and tag.startswith("freemium-"):
                continue
            sys.stderr.write(f"  fetching {tag}...\n")
            body = fetch_release_body(repo, tag)
            prs = parse_prs(body)
            enriched.append({
                "tag": tag,
                "name": r["name"],
                "published_at": r["publishedAt"],
                "is_prerelease": r["isPrerelease"],
                "is_draft": r["isDraft"],
                "body": body,
                "prs": prs,
                "pr_count": len(prs),
            })

        result["repos"][short_name] = {
            "repo": repo,
            "primary_product": primary_product,
            "release_count": len(enriched),
            "pr_count": sum(r["pr_count"] for r in enriched),
            "releases": enriched,
        }

    out_path.write_text(json.dumps(result, indent=2) + "\n")
    sys.stderr.write(f"\nWrote {out_path}\n")
    for short_name, data in result["repos"].items():
        sys.stderr.write(
            f"  {short_name}: {data['release_count']} releases, "
            f"{data['pr_count']} PRs\n"
        )


if __name__ == "__main__":
    main()
