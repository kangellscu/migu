"""Parse index.md and return statistics."""

import sys
from pathlib import Path

def main(kb_dir: str):
    index_file = Path(kb_dir) / "index.md"
    if not index_file.exists():
        print("ERROR: index.md not found", file=sys.stderr)
        sys.exit(1)
    
    content = index_file.read_text()
    lines = content.strip().split("\n")
    
    sections = {}
    current_section = None
    
    for line in lines:
        if line.startswith("## "):
            current_section = line[3:].strip()
            sections[current_section] = []
        elif current_section and line.startswith("- [["):
            sections[current_section].append(line)
    
    doc_counts = {k: len(v) for k, v in sections.items()}
    total_docs = sum(doc_counts.values())
    
    print(f"total:{total_docs}")
    print(f"sections:{','.join(f'{k}:{v}' for k, v in doc_counts.items())}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: read_index.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
