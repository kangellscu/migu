"""Orchestrate lint checks."""

import subprocess
import sys
from pathlib import Path


def main(kb_dir: str):
    scripts_dir = Path(__file__).parent

    # Syntax check
    wiki = Path(kb_dir) / "wiki"
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "syntax.py"), str(wiki)],
        capture_output=True, text=True,
    )
    print("Syntax:", result.stdout.strip())
    syntax_ok = result.returncode == 0

    # Semantic check
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "semantic.py"), str(kb_dir)],
        capture_output=True, text=True,
    )
    print("Semantic:", result.stdout.strip())
    semantic_ok = result.returncode == 0

    if syntax_ok and semantic_ok:
        print("\nAll checks passed ✓")
    else:
        print("\nSome checks failed ✗")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: lint.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
