#!/usr/bin/env python3
"""
inject_links.py — Clean up old Related Studies sections from site index.md files.

Removes the old Related Studies table and any info banners, since the hub
link is now handled by the Material theme announcement bar (overrides/main.html).

Usage:
    python D:/bible/hub-website/inject_links.py --all     # Clean all sites
    python D:/bible/hub-website/inject_links.py --site hist
"""

import argparse
import re
from pathlib import Path

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


def clean_site(site_id, target_path=None):
    """Remove old Related Studies table and info banner from a site."""
    path = target_path or SITE_PATHS.get(site_id)
    if path is None:
        print(f"  ERROR: Unknown site '{site_id}'")
        return False
    if not path.exists():
        print(f"  SKIP: {path} does not exist")
        return False

    content = path.read_text(encoding="utf-8")
    original = content

    # Remove Related Studies section
    content = re.sub(
        r"\n---\n+## Related Studies\n.*?(?=\n## |\Z)",
        "", content, count=1, flags=re.DOTALL
    )
    content = re.sub(
        r"\n## Related Studies\n.*?(?=\n## |\Z)",
        "", content, count=1, flags=re.DOTALL
    )

    # Remove info banner
    content = re.sub(
        r'!!! info "Part of the \[Bible Study Series\].*?\n    .*?\[Browse all series\].*?\.\n*',
        "", content, flags=re.DOTALL
    )

    # Clean up triple+ blank lines
    content = re.sub(r"\n{4,}", "\n\n\n", content)

    if content != original:
        path.write_text(content, encoding="utf-8")
        print(f"  {site_id}: cleaned {path}")
    else:
        print(f"  {site_id}: already clean")
    return True


def main():
    parser = argparse.ArgumentParser(description="Clean old Related Studies from sites")
    parser.add_argument("--site", help="Site ID (e.g. hist, law, etc)")
    parser.add_argument("--target", help="Target index.md path (overrides default)")
    parser.add_argument("--all", action="store_true", help="Clean all sites")
    args = parser.parse_args()

    if args.all:
        print("Cleaning all sites...")
        for site_id in SITE_PATHS:
            clean_site(site_id)
        print("Done.")
    elif args.site:
        target = Path(args.target) if args.target else None
        clean_site(args.site, target)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
