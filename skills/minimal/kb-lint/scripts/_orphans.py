"""Internal module - orphan pages check. Called by lint.py only."""

import sys
import re
from pathlib import Path


def main(kb_dir: str):
    kb = Path(kb_dir)
    if not kb.exists():
        print(f"ERROR: Knowledge base directory not found", file=sys.stderr)
        sys.exit(1)
    
    wiki = kb / "wiki"
    index = kb / "index.md"
    
    if not wiki.exists():
        print(f"ERROR: wiki/ directory not found", file=sys.stderr)
        sys.exit(1)
    
    if not index.exists():
        print(f"ERROR: index.md not found", file=sys.stderr)
        sys.exit(1)
    
    # 1. 扫描 wiki/ 获取所有页面
    wiki_pages = set()
    for md_file in wiki.rglob("*.md"):
        if ".agents" in md_file.parts:
            continue
        wiki_pages.add(md_file.stem)
    
    # 2. 解析 index.md 获取 entries
    index_entries = set()
    index_content = index.read_text(encoding="utf-8")
    wikilink_pattern = re.compile(r'\[\[([^\]]+)\]\]')
    for match in wikilink_pattern.finditer(index_content):
        entry_name = match.group(1).split("|")[0].strip()
        index_entries.add(entry_name)
    
    # 3. 对比找出 orphan pages
    orphans = wiki_pages - index_entries
    
    if orphans:
        print("ORPHAN PAGES:")
        for orphan in sorted(orphans):
            print(f"  {orphan}")
        sys.exit(1)
    else:
        print("ORPHANS OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: _orphans.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])