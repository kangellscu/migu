"""Read report from agent context (stdin or file)."""

import sys
from pathlib import Path

def main(input_source: str = ""):
    if input_source:
        content = Path(input_source).read_text(encoding="utf-8")
    else:
        content = sys.stdin.read()
    
    if not content.strip():
        print("ERROR: No report content found", file=sys.stderr)
        sys.exit(1)
    
    print(content)

if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else ""
    main(source)
