#!/usr/bin/env python3
"""Re-parse PRs in data/releases.json using the current fetch_releases.parse_prs."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_releases import parse_prs  # noqa: E402

root = Path(__file__).resolve().parent.parent
path = root / "data" / "releases.json"
data = json.loads(path.read_text())

for repo_data in data["repos"].values():
    pr_total = 0
    for r in repo_data["releases"]:
        prs = parse_prs(r["body"])
        r["prs"] = prs
        r["pr_count"] = len(prs)
        pr_total += len(prs)
    repo_data["pr_count"] = pr_total

path.write_text(json.dumps(data, indent=2) + "\n")
print(f"Re-parsed {path}")
for short, info in data["repos"].items():
    print(f"  {short}: {info['release_count']} releases, {info['pr_count']} PRs")
