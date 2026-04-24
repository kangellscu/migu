"""Orchestrate lint checks by importing internal modules."""

import sys
from pathlib import Path
import importlib.util


def load_module(module_path: Path):
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(kb_dir: str):
    scripts_dir = Path(__file__).parent
    kb = Path(kb_dir)
    
    if not kb.exists():
        print(f"ERROR: Knowledge base not found: {kb_dir}", file=sys.stderr)
        sys.exit(1)
    
    syntax_module = load_module(scripts_dir / "_syntax.py")
    semantic_module = load_module(scripts_dir / "_semantic.py")
    orphans_module = load_module(scripts_dir / "_orphans.py")
    broken_links_module = load_module(scripts_dir / "_broken_links.py")
    
    print("Running syntax check...")
    syntax_module.main(kb_dir)
    
    print("Running semantic check...")
    semantic_module.main(kb_dir)
    
    print("Running orphan pages check...")
    orphans_module.main(kb_dir)
    
    print("Running broken links check...")
    broken_links_module.main(kb_dir)
    
    print("\nAll checks passed ✓")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: lint.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])