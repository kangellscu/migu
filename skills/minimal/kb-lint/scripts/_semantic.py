"""Internal module - semantic check for wiki pages. Called by lint.py only."""

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

        # Skip YAML frontmatter
        lines = content.strip().split("\n")
        start = 0
        if lines and lines[0] == "---":
            for i, line in enumerate(lines[1:], 1):
                if line == "---":
                    start = i + 1
                    break

        # Check title exists after frontmatter
        title_line = lines[start] if start < len(lines) else ""
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
