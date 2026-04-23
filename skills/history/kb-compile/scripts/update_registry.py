"""Update compilation status in raw-registry.md."""

import sys
from pathlib import Path
from datetime import datetime

def main(kb_dir: str, file_path: str, status: str):
    registry = Path(kb_dir) / "raw-registry.md"
    if not registry.exists():
        print("ERROR: raw-registry.md not found", file=sys.stderr)
        sys.exit(1)
    
    content = registry.read_text()
    lines = content.split("\n")
    today = datetime.now().strftime("%Y-%m-%d")
    
    updated = False
    for i, line in enumerate(lines):
        if file_path in line:
            cells = line.split("|")
            if len(cells) > 6:
                cells[5] = f" {status} "
                cells[6] = f" {today} "
                lines[i] = "|".join(cells)
                updated = True
                break
    
    if updated:
        registry.write_text("\n".join(lines))
        print(f"Updated: {file_path} -> {status}")
    else:
        print(f"WARNING: Entry not found for {file_path}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: update_registry.py <kb_dir> <file_path> <status>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
