"""Normalize markdown file (encoding fix, http image handling)."""

import sys
from pathlib import Path

def main(input_file: str, output_file: str):
    src = Path(input_file)
    dst = Path(output_file)
    dst.parent.mkdir(parents=True, exist_ok=True)

    content = src.read_text(encoding="utf-8")
    needs_fix = False

    if content.startswith('\ufeff'):
        content = content[1:]
        needs_fix = True

    dst.write_text(content, encoding="utf-8")

    if needs_fix:
        print(f"FIXED: {input_file} -> {output_file}")
    else:
        print(f"OK: {input_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: normalize_markdown.py <input> <output>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
