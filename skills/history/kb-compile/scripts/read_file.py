"""Read file content by path."""

import sys
from pathlib import Path

def main(file_path: str):
    p = Path(file_path)
    if not p.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    print(p.read_text(encoding="utf-8"))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: read_file.py <path>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
