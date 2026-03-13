#!/usr/bin/env python3
"""
inject_links.py — Inject Related Studies section into a site's index.md.

Reads related-studies.json from the hub-website repo, excludes the current
site, and replaces (or appends) the Related Studies section in the target
index.md file.

Usage:
    python D:/bible/hub-website/inject_links.py --site hist --target D:/bible/hist-website/docs/index.md
    python D:/bible/hub-website/inject_links.py --site law --target D:/bible/law-website/docs/index.md
    python D:/bible/hub-website/inject_links.py --all     # Update all sites at once
"""

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LINKS_FILE = SCRIPT_DIR / "related-studies.json"

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


def load_links():
    """Load the shared related-studies.json."""
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_section(links, exclude_id):
    """Build the Related Studies markdown section, excluding one site."""
    lines = [
        "## Related Studies",
        "",
        "These companion sites use the same tool-driven research methodology:",
        "",
        "| Site | Description |",
        "|------|-------------|",
    ]
    for entry in links:
        if entry["id"] == exclude_id:
            continue
        lines.append(
            f"| [**{entry['name']}**]({entry['url']}) | {entry['description']} |"
        )
    return "\n".join(lines)


def inject(target_path, section_md):
    """Replace existing Related Studies section or append it."""
    content = target_path.read_text(encoding="utf-8")

    # Pattern: ## Related Studies through to the next ## heading or end of file
    pattern = r"## Related Studies\n.*?(?=\n## |\Z)"
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, section_md, content, count=1, flags=re.DOTALL)
    else:
        # Append at end
        new_content = content.rstrip() + "\n\n---\n\n" + section_md + "\n"

    target_path.write_text(new_content, encoding="utf-8")


def update_site(site_id, target_path=None):
    """Update one site's Related Studies section."""
    links = load_links()
    path = target_path or SITE_PATHS.get(site_id)
    if path is None:
        print(f"  ERROR: Unknown site '{site_id}'")
        return False
    if not path.exists():
        print(f"  SKIP: {path} does not exist")
        return False

    section = build_section(links, site_id)
    inject(path, section)
    print(f"  {site_id}: updated {path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Inject Related Studies links")
    parser.add_argument("--site", help="Site ID to update (e.g. hist, law, etc)")
    parser.add_argument("--target", help="Target index.md path (overrides default)")
    parser.add_argument("--all", action="store_true", help="Update all sites")
    parser.add_argument("--dry-run", action="store_true", help="Print section without writing")
    args = parser.parse_args()

    if args.dry_run and args.site:
        links = load_links()
        print(build_section(links, args.site))
        return

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
