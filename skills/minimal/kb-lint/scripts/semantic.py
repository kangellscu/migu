"""Semantic check: content consistency, template structure."""

import sys
from pathlib import Path


def main(kb_dir: str):
    wiki = Path(kb_dir) / "wiki"
    if not wiki.exists():
        print(f"ERROR: wiki/ directory not found", file=sys.stderr)
        sys.exit(1)

    issues = []
    for md_file in sorted(wiki.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(wiki)

        # Check title matches filename
        title_line = content.strip().split("\n")[0]
        if not title_line.startswith("# "):
            issues.append(f"{rel}: missing title heading")

    if issues:
        print("SEMANTIC ISSUES:")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("SEMANTIC OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: semantic.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
