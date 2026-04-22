"""Syntax check: markdown format, wikilink validity, source field."""

import sys
from pathlib import Path


def main(wiki_dir: str):
    wiki = Path(wiki_dir)
    if not wiki.exists():
        print(f"ERROR: wiki/ directory not found", file=sys.stderr)
        sys.exit(1)

    issues = []
    for md_file in sorted(wiki.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(wiki)

        # Check for source field
        if "## 来源" not in content and "- source:" not in content:
            issues.append(f"{rel}: missing '## 来源' section with source field")

        # Check wikilink format (balanced brackets)
        open_count = content.count("[[")
        close_count = content.count("]]")
        if open_count != close_count:
            issues.append(f"{rel}: unbalanced wikilinks ({open_count} [[ vs {close_count} ]])")

    if issues:
        print("SYNTAX ISSUES:")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("SYNTAX OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: syntax.py <wiki_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
