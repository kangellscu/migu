"""Search wiki directory for matching documents."""

import sys
from pathlib import Path

def main(kb_dir: str, query: str):
    wiki_dir = Path(kb_dir) / "wiki"
    if not wiki_dir.exists():
        print("ERROR: wiki/ directory not found", file=sys.stderr)
        sys.exit(1)

    query_lower = query.lower()
    results = []

    for md_file in sorted(wiki_dir.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8").lower()
        rel_path = md_file.relative_to(wiki_dir)

        if query_lower in content or query_lower in md_file.stem.lower():
            results.append(f"wiki/{rel_path}")

    for r in results:
        print(r)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: search_wiki.py <kb_dir> <query>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
