#!/usr/bin/env python3
"""Fetch title/body/labels/closedAt for every PR referenced in data/releases.json.

Resumable — already-fetched PRs are skipped. Writes to data/prs.json keyed by
"<repo_short>:<number>".

Usage:
    python scripts/fetch_pr_bodies.py [--workers N]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RELEASES_PATH = ROOT / "data" / "releases.json"
DEFAULT_PRS_PATH = ROOT / "data" / "prs.json"

REPO_MAP = {
    "altimate-backend": "AltimateAI/altimate-backend",
    "altimate-frontend": "AltimateAI/altimate-frontend",
    "vscode-dbt-power-user": "AltimateAI/vscode-dbt-power-user",
    "altimate-code": "AltimateAI/altimate-code",
    "altimate-mcp-engine": "AltimateAI/altimate-mcp-engine",
    "vscode-altimate-mcp-server": "AltimateAI/vscode-altimate-mcp-server",
    "altimate-dbt-snowflake-query-tags": "AltimateAI/altimate-dbt-snowflake-query-tags",
}


def fetch_pr(repo: str, number: int) -> dict | None:
    cmd = [
        "gh", "pr", "view", str(number),
        "--repo", repo,
        "--json", "number,title,body,labels,author,closedAt,mergedAt,state,url",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        sys.stderr.write(f"  ! {repo}#{number}: {result.stderr.strip()[:120]}\n")
        return None
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--releases", default=str(DEFAULT_RELEASES_PATH))
    parser.add_argument("--out", default=str(DEFAULT_PRS_PATH))
    args = parser.parse_args()

    RELEASES_PATH = Path(args.releases)
    PRS_PATH = Path(args.out)

    releases_data = json.loads(RELEASES_PATH.read_text())

    # Gather all (short_repo, repo, number) triples
    targets: list[tuple[str, str, int]] = []
    for short_name, info in releases_data["repos"].items():
        repo = REPO_MAP[short_name]
        for r in info["releases"]:
            for pr in r["prs"]:
                targets.append((short_name, repo, pr["number"]))

    # Dedupe (PR can appear in only one release, but safe-guard)
    seen = set()
    unique = []
    for t in targets:
        key = (t[0], t[2])
        if key in seen:
            continue
        seen.add(key)
        unique.append(t)

    # Load existing cache
    cache: dict[str, dict] = {}
    if PRS_PATH.exists():
        cache = json.loads(PRS_PATH.read_text())

    to_fetch = [
        (short, repo, num) for short, repo, num in unique
        if f"{short}:{num}" not in cache
    ]
    sys.stderr.write(
        f"Total PRs: {len(unique)}; cached: {len(cache)}; to fetch: {len(to_fetch)}\n"
    )

    if not to_fetch:
        sys.stderr.write("Nothing to fetch.\n")
        return

    start = time.time()
    completed = 0
    save_every = 50

    def task(t):
        short, repo, num = t
        data = fetch_pr(repo, num)
        return short, num, data

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(task, t) for t in to_fetch]
        for fut in as_completed(futures):
            short, num, data = fut.result()
            key = f"{short}:{num}"
            cache[key] = data or {"_error": True, "number": num, "repo": short}
            completed += 1
            if completed % save_every == 0:
                PRS_PATH.write_text(json.dumps(cache, indent=2) + "\n")
                rate = completed / (time.time() - start)
                eta = (len(to_fetch) - completed) / rate if rate else 0
                sys.stderr.write(
                    f"  [{completed}/{len(to_fetch)}] "
                    f"rate={rate:.1f}/s eta={eta:.0f}s\n"
                )

    PRS_PATH.write_text(json.dumps(cache, indent=2) + "\n")
    elapsed = time.time() - start
    sys.stderr.write(
        f"Done. Fetched {completed} PRs in {elapsed:.0f}s. Cache: {PRS_PATH}\n"
    )


if __name__ == "__main__":
    main()
