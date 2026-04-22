"""Update entity wiki file with organic integration."""

import sys
from pathlib import Path

def main(entity_path: str, content: str):
    p = Path(entity_path)
    if not p.exists():
        print(f"ERROR: Entity file not found: {entity_path}", file=sys.stderr)
        sys.exit(1)
    
    existing = p.read_text(encoding="utf-8")
    
    # Append to end before source section
    if "## 来源" in existing:
        parts = existing.split("## 来源", 1)
        updated = parts[0].rstrip() + "\n\n" + content + "\n\n## 来源" + parts[1]
    else:
        updated = existing.rstrip() + "\n\n" + content + "\n"
    
    p.write_text(updated, encoding="utf-8")
    print(f"Updated: {entity_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: update_entity.py <entity_path> <content>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
