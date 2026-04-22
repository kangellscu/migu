"""Auto-fix fixable lint issues."""

import sys
from pathlib import Path


def main(kb_dir: str):
    wiki = Path(kb_dir) / "wiki"
    if not wiki.exists():
        print("ERROR: wiki/ directory not found", file=sys.stderr)
        sys.exit(1)

    fixed = 0
    for md_file in wiki.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        original = content

        # Fix wikilink imbalance (remove orphan brackets)
        while "[[" in content and "]]" not in content:
            content = content.replace("[[", "", 1)
        while "]]" in content and "[[" not in content:
            content = content.replace("]]", "", 1)

        # Add missing source placeholder
        if "## 来源" not in content and "- source:" not in content:
            content = content.rstrip() + "\n\n## 来源\n- source: [[raw/PENDING]]\n"

        if content != original:
            md_file.write_text(content, encoding="utf-8")
            print(f"Fixed: {md_file.relative_to(wiki)}")
            fixed += 1

    print(f"Fixed {fixed} files")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: fix.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
