#!/usr/bin/env python3
"""Generate proposed changelog entries from data/features.json.

Writes Markdown files to `generated/` (NOT `entries/`), with one file per
feature group. Frontmatter matches the schema in products.yml + STYLE.md.

The generated content is a *draft* — titles/bodies pull from PR data and
will not match the polished customer-facing voice required by STYLE.md.
Use these as a starting point and edit/promote into entries/ manually.

Usage:
    python scripts/generate_entries.py [--limit N] [--sample]
        --sample writes only 5 demo files for review.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEATURES_PATH = ROOT / "data" / "features.json"
OUT_DIR = ROOT / "generated"

# Map from internal product slugs (must match products.yml)
VALID_PRODUCTS = {
    "dbt-power-user", "snowflake-app", "databricks-app",
    "altimate-code", "datamates",
}

EMOJI_BY_KEYWORD = [
    (re.compile(r"(?i)\b(cost|saving|spend|budget|billing|dbu)\b"), "💰"),
    (re.compile(r"(?i)\b(alert|notification|email|slack|subscribe)\b"), "🔔"),
    (re.compile(r"(?i)\b(filter|search|sort|column)\b"), "🔎"),
    (re.compile(r"(?i)\b(dashboard|chart|graph|visual|insight)\b"), "📊"),
    (re.compile(r"(?i)\b(auto[\s-]?tune|tune|optimi[sz]e|recommendation)\b"), "🤖"),
    (re.compile(r"(?i)\b(query|sql|warehouse)\b"), "🗄️"),
    (re.compile(r"(?i)\b(job|task|workload|schedule)\b"), "⏱️"),
    (re.compile(r"(?i)\b(studio|prompt|agent|knowledge)\b"), "✨"),
    (re.compile(r"(?i)\b(lineage|catalog|metadata)\b"), "🔗"),
    (re.compile(r"(?i)\b(security|sso|auth|permission|access)\b"), "🔐"),
    (re.compile(r"(?i)\b(databricks|spark|photon|dbx)\b"), "🧱"),
    (re.compile(r"(?i)\b(snowflake)\b"), "❄️"),
    (re.compile(r"(?i)\b(dbt)\b"), "🧰"),
]
DEFAULT_EMOJI = "🚀"


def pick_emoji(text: str) -> str:
    for pat, emoji in EMOJI_BY_KEYWORD:
        if pat.search(text):
            return emoji
    return DEFAULT_EMOJI


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]+", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s[:60] or "untitled"


def first_paragraph(body: str) -> str:
    """Pull the first meaningful paragraph from a PR body."""
    if not body:
        return ""
    cleaned = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    # Skip standard headings like "## Summary"
    paragraphs = []
    for chunk in re.split(r"\n\s*\n", cleaned.strip()):
        chunk = chunk.strip()
        if not chunk:
            continue
        # Skip pure headings
        if re.match(r"^#+\s+\w+\s*$", chunk):
            continue
        # Skip code/tables/checkboxes-only blocks
        if chunk.startswith("```") or chunk.startswith("|"):
            continue
        paragraphs.append(chunk)
        if len(paragraphs) >= 2:
            break
    if not paragraphs:
        return ""
    # Drop heading prefix like "## Summary\n..." -> keep body
    out = "\n\n".join(paragraphs)
    out = re.sub(r"^#+\s+[\w\s]+\n+", "", out)
    # Strip Jira links / internal markers
    out = re.sub(r"\[?AI-\d{2,5}\]?", "", out)
    out = re.sub(r"@[\w-]+", "", out)
    # Trim
    out = re.sub(r"\s+", " ", out).strip()
    return out


def normalize_products(products: list[str]) -> list[str]:
    keep = [p for p in products if p in VALID_PRODUCTS]
    return keep or ["snowflake-app"]  # default per user's note


def build_entry(feature: dict) -> tuple[str, str]:
    title = feature["title"].strip()
    # Strip lingering noise
    title = re.sub(r"\(#?\d+\)$", "", title).strip()
    title = re.sub(r"^\W+", "", title)
    # Capitalize first letter
    title = title[:1].upper() + title[1:] if title else "Untitled"
    if len(title) > 80:
        title = title[:77] + "..."

    date = (feature.get("latest_published_at") or "")[:10]
    products = normalize_products(feature.get("products") or [])
    tag = "new"  # we filtered to feat: prefix
    emoji = pick_emoji(title)
    slug = slugify(title)
    filename = f"{date}-{slug}.md"

    # Body: pick the longest first-paragraph from any PR in the group
    bodies = [(first_paragraph(p.get("title_raw", "")), first_paragraph(_load_body(p)))
              for p in feature["prs"]]
    body_candidates = []
    for _, b in bodies:
        if b and 40 < len(b) < 400:
            body_candidates.append(b)
    body = max(body_candidates, key=len, default="")
    if not body:
        # Fall back to title as the body
        body = title

    pr_links = "\n".join(
        f"- [{p['repo'].replace('altimate-', '')}#{p['number']}]({p['url']}) — {p['title']}"
        for p in feature["prs"][:6]
    )

    frontmatter = (
        "---\n"
        f"title: {title}\n"
        f"date: {date}\n"
        f"products: [{', '.join(products)}]\n"
        f"tag: {tag}\n"
        f"emoji: {emoji}\n"
        "draft: true\n"
        f"description: {body[:180]}\n"
        "---\n\n"
    )
    content = (
        f"{body}\n\n"
        f"<!-- source PRs (remove before publishing):\n{pr_links}\n-->\n"
    )
    return filename, frontmatter + content


_pr_body_cache: dict[str, str] = {}


def _load_body(pr_summary: dict) -> str:
    """Look up full PR body from data/prs.json on demand."""
    if not _pr_body_cache:
        prs = json.loads((ROOT / "data" / "prs.json").read_text())
        for k, v in prs.items():
            _pr_body_cache[k] = (v or {}).get("body") or ""
    key = f"{pr_summary['repo']}:{pr_summary['number']}"
    return _pr_body_cache.get(key, "")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sample", action="store_true",
                        help="Write only 5 demo files for review.")
    args = parser.parse_args()

    OUT_DIR.mkdir(exist_ok=True)

    data = json.loads(FEATURES_PATH.read_text())
    features = data["features"]
    if args.sample:
        features = features[:5]
    elif args.limit:
        features = features[: args.limit]

    seen_filenames: set[str] = set()
    written = 0
    for feat in features:
        filename, content = build_entry(feat)
        # Dedupe filenames
        base = filename
        idx = 2
        while filename in seen_filenames:
            filename = base.replace(".md", f"-{idx}.md")
            idx += 1
        seen_filenames.add(filename)
        (OUT_DIR / filename).write_text(content)
        written += 1

    print(f"Wrote {written} entries to {OUT_DIR}/")


if __name__ == "__main__":
    main()
