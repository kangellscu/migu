"""Validate batch processing results."""

import sys
from pathlib import Path

def main(kb_dir: str):
    registry = Path(kb_dir) / "raw-registry.md"
    if not registry.exists():
        print("ERROR: raw-registry.md not found", file=sys.stderr)
        sys.exit(1)

    content = registry.read_text()
    lines = content.split("\n")
    issues = []

    for i, line in enumerate(lines, 1):
        if "[[" in line and line.count("[[") != line.count("]]"):
            issues.append(f"Line {i}: wikilink format error, expected [[path|alias]]")
        if "状态" in line and "预处理" in line:
            continue
        if line.startswith("|------"):
            continue

    if issues:
        print("VALIDATION_FAILED:")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("VALID")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_batch.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
