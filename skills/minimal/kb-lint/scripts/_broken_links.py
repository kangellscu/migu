"""Internal module - broken wikilinks check. Called by lint.py only."""

import sys
import re
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
    
    # 1. 收集 wiki/ 中所有页面名称
    wiki_pages = set()
    for md_file in wiki.rglob("*.md"):
        if ".agents" in md_file.parts:
            continue
        wiki_pages.add(md_file.stem)
    
    # 2. 解析每个页面的 wikilinks，验证引用是否存在
    issues_by_file = {}
    wikilink_pattern = re.compile(r'\[\[([^\]]+)\]\]')
    
    for md_file in wiki.rglob("*.md"):
        if ".agents" in md_file.parts:
            continue
        
        content = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(wiki)
        
        # 排除 source 字段的引用（source: [[raw/...]]）
        for match in wikilink_pattern.finditer(content):
            link = match.group(1)
            
            # 排除 raw/ 路径（source 字段）
            if link.startswith("raw/"):
                continue
            
            # 提取页面名称（去除 display text）
            page_name = link.split("|")[0].strip()
            
            # 验证引用是否存在
            if page_name not in wiki_pages:
                if str(rel) not in issues_by_file:
                    issues_by_file[str(rel)] = []
                issues_by_file[str(rel)].append(f"[[{page_name}]]")
    
    if issues_by_file:
        print("BROKEN LINKS:")
        for file in sorted(issues_by_file.keys()):
            links = issues_by_file[file]
            print(f"  - {file}")
            print(f"    {', '.join(links)}")
        sys.exit(1)
    else:
        print("BROKEN LINKS OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: _broken_links.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])