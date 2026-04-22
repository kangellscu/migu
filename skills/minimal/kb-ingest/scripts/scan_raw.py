"""Scan raw/ directory and detect new files."""

import sys
from pathlib import Path

def main(kb_dir: str):
    raw_dir = Path(kb_dir) / "raw"
    if not raw_dir.exists():
        print("ERROR: raw/ directory not found", file=sys.stderr)
        sys.exit(1)

    extracted_dir = raw_dir / ".extracted"
    files = [f for f in raw_dir.rglob("*") if f.is_file() and not str(f).startswith(str(extracted_dir))]

    for f in sorted(files):
        rel_path = f.relative_to(raw_dir)
        ext = f.suffix.lower()
        if ext in (".md",):
            file_type = "markdown"
        elif ext == ".pdf":
            file_type = "pdf"
        elif ext in (".png", ".jpg", ".jpeg", ".gif"):
            file_type = "image"
        else:
            file_type = "unknown"
        print(f"{rel_path}|{file_type}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: scan_raw.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
