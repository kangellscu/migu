"""Auto-fix fixable lint issues."""

import sys
from pathlib import Path


def parse_registry(registry_file: Path) -> dict:
    if not registry_file.exists():
        return {}
    
    content = registry_file.read_text()
    lines = content.strip().split("\n")
    
    data_lines = []
    in_table = False
    for line in lines:
        if line.startswith("|") and "-" in line and line.replace("|", "").replace("-", "").replace(" ", "") == "":
            in_table = True
            continue
        if in_table and line.strip():
            data_lines.append(line)
    
    registry = {}
    for line in data_lines:
        cells = []
        current = ""
        in_wiki_link = False
        
        for i, char in enumerate(line):
            if i >= 2 and line[i-2:i] == "[[":
                in_wiki_link = True
            if in_wiki_link and i >= 2 and line[i-2:i] == "]]":
                in_wiki_link = False
            
            if char == "|" and not in_wiki_link:
                cells.append(current.strip())
                current = ""
            else:
                current += char
        
        if current.strip():
            cells.append(current.strip())
        
        cells = cells[1:] if cells else []
        if len(cells) >= 7:
            file_path = cells[0]
            product_path = cells[4]
            if product_path:
                registry[product_path] = file_path
    
    return registry


def main(kb_dir: str):
    kb = Path(kb_dir)
    wiki = kb / "wiki"
    
    if not wiki.exists():
        print("ERROR: wiki/ directory not found", file=sys.stderr)
        sys.exit(1)
    
    registry = parse_registry(kb / "raw-registry.md")
    
    fixed = 0
    for md_file in wiki.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        original = content

        while "[[" in content and "]]" not in content:
            content = content.replace("[[", "", 1)
        while "]]" in content and "[[" not in content:
            content = content.replace("]]", "", 1)

        if "## 来源" not in content and "- source:" not in content:
            rel_path = str(md_file.relative_to(wiki))
            source_path = registry.get(rel_path)
            
            if source_path:
                source_link = f"[[raw/{source_path}]]"
                content = content.rstrip() + f"\n\n## 来源\n- source: {source_link}\n"
            else:
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