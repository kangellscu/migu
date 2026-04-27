"""Create synthesis report file."""

import sys
from pathlib import Path
from datetime import datetime


def strip_frontmatter(content: str) -> str:
    """Remove existing frontmatter from content.

    Handles YAML frontmatter enclosed by --- markers.
    Returns content without frontmatter section.
    """
    if content.strip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content.strip()


def main(synthesis_dir: str, title: str):
    out_dir = Path(synthesis_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Read report from stdin
    content = sys.stdin.read()
    clean_content = strip_frontmatter(content)

    title_line = f"# {title}"
    date_str = datetime.now().strftime("%Y-%m-%d")

    output = f"---\ntitle: {title}\ntype: synthesis\ndate: {date_str}\n---\n\n{clean_content}\n"
    
    out_file = out_dir / f"{title}.md"
    out_file.write_text(output, encoding="utf-8")
    print(f"Created: {out_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: create_synthesis.py <synthesis_dir> <title>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
