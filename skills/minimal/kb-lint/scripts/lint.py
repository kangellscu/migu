"""Orchestrate lint checks with structured reporting."""

import sys
import argparse
from pathlib import Path
import importlib.util

from _report import LintReport, Issue, print_report


def load_module(module_path: Path):
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_format_checks(kb_dir: str, report: LintReport):
    """Run format-level checks (deterministic, auto-fixable)."""
    kb = Path(kb_dir)
    wiki = kb / "wiki"
    
    if not wiki.exists():
        return
    
    for md_file in wiki.rglob("*.md"):
        if ".agents" in md_file.parts:
            continue
        
        content = md_file.read_text(encoding="utf-8")
        rel = str(md_file.relative_to(wiki))
        
        open_count = content.count("[[")
        close_count = content.count("]]")
        if open_count != close_count:
            report.format_issues.append(Issue(
                category="格式",
                problem="wikilink 不平衡",
                file=rel,
                suggestion=f"移除孤立的括号（{open_count} [[ vs {close_count} ]]）"
            ))
        
        if "## 来源" not in content and "- source:" not in content:
            report.format_issues.append(Issue(
                category="格式",
                problem="缺失 source",
                file=rel,
                suggestion="添加 ## 来源 section"
            ))


def run_structure_checks(kb_dir: str, report: LintReport):
    """Run structure-level checks (inferable, needs confirmation)."""
    kb = Path(kb_dir)
    wiki = kb / "wiki"
    index = kb / "index.md"
    
    if not wiki.exists() or not index.exists():
        return
    
    import re
    
    wiki_pages = {}
    for md_file in wiki.rglob("*.md"):
        if ".agents" in md_file.parts:
            continue
        wiki_pages[md_file.stem] = md_file.relative_to(wiki)
    
    index_entries = set()
    index_content = index.read_text(encoding="utf-8")
    wikilink_pattern = re.compile(r'\[\[([^\]]+)\]\]')
    for match in wikilink_pattern.finditer(index_content):
        entry_name = match.group(1).split("|")[0].strip()
        index_entries.add(entry_name)
    
    orphans = set(wiki_pages.keys()) - index_entries
    for orphan in sorted(orphans):
        orphan_path = wiki_pages[orphan]
        suggestion = suggest_section(str(orphan_path))
        report.structure_issues.append(Issue(
            category="结构",
            problem="orphan page",
            file=str(orphan_path),
            suggestion=suggestion
        ))
    
    wikilink_pattern = re.compile(r'\[\[([^\]]+)\]\]')
    for md_file in wiki.rglob("*.md"):
        if ".agents" in md_file.parts:
            continue
        
        content = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(wiki)
        
        broken = []
        for match in wikilink_pattern.finditer(content):
            link = match.group(1)
            
            if link.startswith("raw/"):
                continue
            
            page_name = link.split("|")[0].strip()
            
            if page_name not in wiki_pages:
                broken.append(f"[[{page_name}]]")
        
        if broken:
            report.structure_issues.append(Issue(
                category="结构",
                problem=f"broken wikilinks: {', '.join(broken)}",
                file=str(rel),
                suggestion="创建缺失页面或删除链接"
            ))
    
    for md_file in sorted(wiki.rglob("*.md")):
        if ".agents" in md_file.parts:
            continue
        
        content = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(wiki)
        
        lines = content.strip().split("\n")
        start = 0
        if lines and lines[0] == "---":
            for i, line in enumerate(lines[1:], 1):
                if line == "---":
                    start = i + 1
                    break
        
        title_line = lines[start] if start < len(lines) else ""
        if not title_line.startswith("# "):
            suggestion = f"添加标题: # {md_file.stem}"
            report.structure_issues.append(Issue(
                category="结构",
                problem="缺失 title heading",
                file=str(rel),
                suggestion=suggestion
            ))


def run_content_checks(kb_dir: str, report: LintReport):
    """Run content-level checks (semantic, requires LLM)."""
    pass


def suggest_section(orphan_path: str) -> str:
    """Suggest which section an orphan page should be added to."""
    parts = Path(orphan_path).parts
    
    if len(parts) >= 2:
        parent_dir = parts[-2]
        return f"添加到 \"{parent_dir}\" section"
    elif len(parts) == 1:
        return "添加到合适的 section"
    else:
        return "添加到 index.md"


def main():
    parser = argparse.ArgumentParser(description="Lint wiki pages with structured reporting")
    parser.add_argument("kb_dir", help="Knowledge base directory")
    parser.add_argument("--mode", choices=["summary", "detailed"], default="summary",
                       help="Report mode: summary (default) or detailed")
    args = parser.parse_args()
    
    kb = Path(args.kb_dir)
    
    if not kb.exists():
        print(f"ERROR: Knowledge base not found: {args.kb_dir}", file=sys.stderr)
        sys.exit(1)
    
    report = LintReport()
    
    print("Running format checks...", file=sys.stderr)
    run_format_checks(args.kb_dir, report)
    
    print("Running structure checks...", file=sys.stderr)
    run_structure_checks(args.kb_dir, report)
    
    print("Running content checks...", file=sys.stderr)
    run_content_checks(args.kb_dir, report)
    
    print_report(report, args.mode)
    
    if report.format_issues or report.structure_issues or report.content_issues:
        sys.exit(1)


if __name__ == "__main__":
    main()