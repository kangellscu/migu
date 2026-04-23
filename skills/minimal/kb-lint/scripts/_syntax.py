"""Internal module - syntax check for wiki pages. Called by lint.py only."""

import sys
from pathlib import Path


def main(kb_dir: str):
    kb = Path(kb_dir)
    if not kb.exists():
        print(f"ERROR: Knowledge base directory not found", file=sys.stderr)
        sys.exit(1)
    
    wiki = kb / "wiki"
    if not wiki.exists():
        print(f"ERROR: wiki/ directory not found", file=sys.stderr)
        sys.exit(1)
    
    issues = []
    for md_file in sorted(wiki.rglob("*.md")):
        if ".agents" in md_file.parts:
            continue
        
        content = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(wiki)

        if "## 来源" not in content and "- source:" not in content:
            issues.append(f"{rel}: missing '## 来源' section with source field")

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
        print("Usage: syntax.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])