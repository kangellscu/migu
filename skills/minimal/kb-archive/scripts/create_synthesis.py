"""Create synthesis report file."""

import sys
from pathlib import Path
from datetime import datetime

def main(synthesis_dir: str, title: str):
    out_dir = Path(synthesis_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Read report from stdin
    content = sys.stdin.read()
    
    title_line = f"# {title}"
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    output = f"---\ntitle: {title}\ntype: synthesis\ndate: {date_str}\n---\n\n{content}\n"
    
    out_file = out_dir / f"{title}.md"
    out_file.write_text(output, encoding="utf-8")
    print(f"Created: {out_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: create_synthesis.py <synthesis_dir> <title>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
