#!/usr/bin/env python3
"""Read `data/curation.md`, extract `[x]`-marked features, write drafts to `generated/`.

Reads:
  data/curation.md
  data/features.json
  data/prs.json

Writes:
  generated/YYYY-MM-DD-<slug>.md (one per marked feature, deduped)

The "polish" applied here is rule-based:
  - Strip `feat:` / `fix:` / `[AI-XXXX]` / `(#1234)` prefixes/suffixes
  - Pull the first meaningful paragraph from the longest PR body
  - Strip Jira links, @mentions, internal headings
  - Truncate description to ≤200 chars (CI validator's limit)
  - Default `draft: true` so the website skips entries until human-reviewed

For true STYLE.md voice rewrites (active voice, no marketing-speak), run each
draft through Claude in a subsequent pass.

Usage:
    python scripts/polish_entries.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURATION_PATH = ROOT / "data" / "curation.md"
FEATURES_PATH = ROOT / "data" / "features.json"
PRS_PATH = ROOT / "data" / "prs.json"
OUT_DIR = ROOT / "generated"

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

MARK_RE = re.compile(r"^- \[x\] `([^`]+)`", re.IGNORECASE)


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]+", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s[:60] or "untitled"


def pick_emoji(text: str) -> str:
    for pat, emoji in EMOJI_BY_KEYWORD:
        if pat.search(text):
            return emoji
    return "🚀"


def clean_title(title: str) -> str:
    t = title.strip()
    t = re.sub(r"^\s*(feat|fix|chore|test|ci|docs|build|perf|refactor|revert|style)"
               r"(?:\([^)]*\))?\s*:\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\[?AI-\d{2,5}\]?", "", t)
    t = re.sub(r"\(#\d+\)$", "", t).strip()
    t = re.sub(r"\s+", " ", t)
    if t:
        t = t[:1].upper() + t[1:]
    return t.strip()


def first_paragraph(body: str) -> str:
    if not body:
        return ""
    cleaned = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    paragraphs = []
    for chunk in re.split(r"\n\s*\n", cleaned.strip()):
        chunk = chunk.strip()
        if not chunk:
            continue
        if re.match(r"^#+\s+\w+\s*$", chunk):  # bare heading
            continue
        if chunk.startswith("```") or chunk.startswith("|"):
            continue
        # Skip task lists / checkboxes
        if chunk.lstrip().startswith("- [ ]") or chunk.lstrip().startswith("- [x]"):
            continue
        paragraphs.append(chunk)
        if len(paragraphs) >= 2:
            break
    if not paragraphs:
        return ""
    out = "\n\n".join(paragraphs)
    out = re.sub(r"^#+\s+[\w\s]+\n+", "", out)
    out = re.sub(r"\[?AI-\d{2,5}\]?", "", out)
    out = re.sub(r"@[\w-]+", "", out)
    out = re.sub(r"https?://altimateai\.atlassian\.net/[^\s)]+", "", out)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def normalize_products(products: list[str]) -> list[str]:
    keep = [p for p in products if p in VALID_PRODUCTS]
    return keep or ["snowflake-app"]


def truncate_for_description(text: str, limit: int = 180) -> str:
    text = text.strip().replace("\n", " ")
    if len(text) <= limit:
        return text
    # Cut at sentence boundary if possible
    cut = text[:limit]
    last_period = cut.rfind(". ")
    if last_period > 80:
        return cut[: last_period + 1]
    return cut.rsplit(" ", 1)[0] + "..."


def build_entry(feat: dict, pr_bodies: dict[str, str]) -> tuple[str, str]:
    title = clean_title(feat["title"])
    if len(title) > 80:
        title = title[:77] + "..."

    date = (feat.get("latest_published_at") or "")[:10]
    products = normalize_products(feat.get("products") or [])
    tag = "new"
    emoji = pick_emoji(title)
    slug = slugify(title)
    filename = f"{date}-{slug}.md"

    body_candidates: list[str] = []
    for p in feat["prs"]:
        key = f"{p['repo']}:{p['number']}"
        bp = first_paragraph(pr_bodies.get(key, ""))
        if bp and 60 < len(bp) < 800:
            body_candidates.append(bp)
    body = max(body_candidates, key=len, default=title)
    description = truncate_for_description(body)

    pr_links = "\n".join(
        f"- [{p['repo'].replace('altimate-', '')}#{p['number']}]({p['url']}) — "
        f"{clean_title(p['title'])}"
        for p in feat["prs"][:8]
    )

    frontmatter = (
        "---\n"
        f"title: {title}\n"
        f"date: {date}\n"
        f"products: [{', '.join(products)}]\n"
        f"tag: {tag}\n"
        f"emoji: {emoji}\n"
        "draft: true\n"
        f"description: {description}\n"
        "---\n\n"
    )
    content = (
        f"{body}\n\n"
        f"<!-- source PRs (review and remove before publishing):\n{pr_links}\n-->\n"
    )
    return filename, frontmatter + content


def parse_marks(curation: str) -> list[str]:
    ids: list[str] = []
    for line in curation.splitlines():
        m = MARK_RE.match(line.strip())
        if m:
            ids.append(m.group(1))
    return ids


def main() -> None:
    curation = CURATION_PATH.read_text()
    marked_ids = parse_marks(curation)
    print(f"Marked features: {len(marked_ids)}")
    if not marked_ids:
        print("No `[x]` marks found in data/curation.md. Edit it first.")
        return

    features = json.loads(FEATURES_PATH.read_text())["features"]
    by_id = {f["id"]: f for f in features}

    prs = json.loads(PRS_PATH.read_text())
    pr_bodies = {k: (v or {}).get("body") or "" for k, v in prs.items()}

    OUT_DIR.mkdir(exist_ok=True)
    written = 0
    skipped = 0
    seen_filenames: set[str] = set()

    for fid in marked_ids:
        feat = by_id.get(fid)
        if not feat:
            print(f"  WARN: unknown id {fid!r}, skipping")
            skipped += 1
            continue
        filename, content = build_entry(feat, pr_bodies)
        base = filename
        idx = 2
        while filename in seen_filenames:
            filename = base.replace(".md", f"-{idx}.md")
            idx += 1
        seen_filenames.add(filename)
        (OUT_DIR / filename).write_text(content)
        written += 1

    print(f"Wrote {written} entries to {OUT_DIR}/")
    if skipped:
        print(f"  skipped {skipped} unknown ids")


if __name__ == "__main__":
    main()
