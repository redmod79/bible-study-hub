#!/usr/bin/env python3
"""
inject_links.py — Inject a hub link into each site's index.md.

Replaces the old "Related Studies" table with a single link back to the
Bible Study Hub. Also adds a hub banner near the top of the page (after
the first heading/subtitle block).

Usage:
    python D:/bible/hub-website/inject_links.py --all     # Update all sites at once
    python D:/bible/hub-website/inject_links.py --site hist
"""

import argparse
import re
from pathlib import Path

HUB_URL = "https://redmod79.github.io/bible-study-hub/"

HUB_BANNER = (
    '!!! info "Part of the [Bible Study Series]({url})"\n'
    "    This study is one of several series using the same tool-driven, "
    "sola scriptura research methodology. "
    "[Browse all series]({url})."
).format(url=HUB_URL)

# Map site IDs to their index.md paths
SITE_PATHS = {
    "hist": Path("D:/bible/hist-website/docs/index.md"),
    "law": Path("D:/bible/law-website/docs/index.md"),
    "etc": Path("D:/bible/etc-website/docs/index.md"),
    "pvj": Path("D:/bible/pvj-website/docs/index.md"),
    "cmd": Path("D:/bible/cmd-website/docs/index.md"),
    "genesis-6": Path("D:/bible/genesis-6-website/docs/index.md"),
    "bible-topics": Path("D:/bible/bible-topics-website/docs/index.md"),
}


def remove_related_studies(content):
    """Remove the old Related Studies section entirely."""
    # Match: ---\n\n## Related Studies ... to end or next ## heading
    # Also remove the preceding --- separator if present
    pattern = r"\n---\n+## Related Studies\n.*?(?=\n## |\Z)"
    content = re.sub(pattern, "", content, count=1, flags=re.DOTALL)
    # Also catch without preceding ---
    pattern2 = r"\n## Related Studies\n.*?(?=\n## |\Z)"
    content = re.sub(pattern2, "", content, count=1, flags=re.DOTALL)
    return content


def inject_banner(content):
    """Add hub banner after the first paragraph block (after title + intro)."""
    # If banner already exists, remove it first
    content = re.sub(
        r'!!! info "Part of the \[Bible Study Series\].*?\n    \[Browse all series\].*?\.\n*',
        "",
        content,
        flags=re.DOTALL,
    )

    # Insert after the first --- separator (which comes after the intro paragraph)
    # This places it prominently near the top
    first_sep = content.find("\n---\n")
    if first_sep != -1:
        # Insert banner right after the first ---
        insert_pos = first_sep + len("\n---\n")
        content = content[:insert_pos] + "\n" + HUB_BANNER + "\n\n" + content[insert_pos:].lstrip("\n")
    else:
        # No separator found, insert after the first blank line (after title)
        first_blank = content.find("\n\n")
        if first_blank != -1:
            insert_pos = first_blank + 2
            content = content[:insert_pos] + HUB_BANNER + "\n\n" + content[insert_pos:]

    return content


def update_site(site_id, target_path=None):
    """Update one site: remove Related Studies table, add hub banner."""
    path = target_path or SITE_PATHS.get(site_id)
    if path is None:
        print(f"  ERROR: Unknown site '{site_id}'")
        return False
    if not path.exists():
        print(f"  SKIP: {path} does not exist")
        return False

    content = path.read_text(encoding="utf-8")
    content = remove_related_studies(content)
    content = inject_banner(content)
    # Clean up any triple+ blank lines
    content = re.sub(r"\n{4,}", "\n\n\n", content)
    path.write_text(content, encoding="utf-8")
    print(f"  {site_id}: updated {path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Inject hub link into sites")
    parser.add_argument("--site", help="Site ID to update (e.g. hist, law, etc)")
    parser.add_argument("--target", help="Target index.md path (overrides default)")
    parser.add_argument("--all", action="store_true", help="Update all sites")
    args = parser.parse_args()

    if args.all:
        print("Updating all sites...")
        for site_id in SITE_PATHS:
            update_site(site_id)
        print("Done.")
    elif args.site:
        target = Path(args.target) if args.target else None
        update_site(args.site, target)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
