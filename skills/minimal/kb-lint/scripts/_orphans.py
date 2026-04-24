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
    wiki_pages_by_stem = {}
    for md_file in wiki.rglob("*.md"):
        if ".agents" in md_file.parts:
            continue
        wiki_pages_by_stem[md_file.stem] = md_file
    
    # 2. 解析 index.md 获取 entries
    index_entries = set()
    index_content = index.read_text(encoding="utf-8")
    wikilink_pattern = re.compile(r'\[\[([^\]]+)\]\]')
    for match in wikilink_pattern.finditer(index_content):
        entry_name = match.group(1).split("|")[0].strip()
        index_entries.add(entry_name)
    
    # 3. 对比找出 orphan pages
    orphans = set(wiki_pages_by_stem.keys()) - index_entries
    
    if orphans:
        print("ORPHAN PAGES:")
        for orphan in sorted(orphans):
            orphan_path = wiki_pages_by_stem.get(orphan)
            if orphan_path:
                suggestion = suggest_section(str(orphan_path.relative_to(wiki)))
                print(f"  {orphan_path.relative_to(wiki)} ({suggestion})")
            else:
                print(f"  {orphan}")
        sys.exit(1)
    else:
        print("ORPHANS OK")


def suggest_section(orphan_path: str) -> str:
    parts = Path(orphan_path).parts
    
    if len(parts) >= 2:
        parent_dir = parts[-2]
        return f"建议: 添加到 \"{parent_dir}\" section"
    elif len(parts) == 1:
        return "建议: 添加到合适的 section"
    else:
        return "建议: 添加到 index.md"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: _orphans.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])