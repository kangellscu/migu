"""Internal module - generate structured lint reports. Called by lint.py only."""

from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path


@dataclass
class Issue:
    category: str
    problem: str
    file: str
    suggestion: str = ""


@dataclass  
class LintReport:
    format_issues: List[Issue] = field(default_factory=list)
    structure_issues: List[Issue] = field(default_factory=list)
    content_issues: List[Issue] = field(default_factory=list)

    def summary(self) -> str:
        lines = ["kb-lint Summary", ""]
        
        format_count = len(self.format_issues)
        structure_count = len(self.structure_issues)
        content_count = len(self.content_issues)
        
        lines.append(f"- 格式问题: {format_count} 个（可自动修复）")
        format_breakdown = self._breakdown_by_problem(self.format_issues)
        for problem, count in format_breakdown.items():
            lines.append(f"  - {problem}: {count}")
        
        lines.append("")
        lines.append(f"- 结构问题: {structure_count} 个（建议修复）")
        structure_breakdown = self._breakdown_by_problem(self.structure_issues)
        for problem, count in structure_breakdown.items():
            lines.append(f"  - {problem}: {count}")
        
        lines.append("")
        lines.append(f"- 内容问题: {content_count} 个（需人工修复）")
        
        lines.append("")
        lines.append('Next: "lint 详细" 查看完整报告，或 "lint 并修复" 自动修复格式问题')
        
        return "\n".join(lines)

    def detailed(self) -> str:
        lines = ["kb-lint Report", ""]
        
        lines.append("## 问题概览")
        lines.append(f"- 格式问题: {len(self.format_issues)} 个（可自动修复）")
        lines.append(f"- 结构问题: {len(self.structure_issues)} 个（建议修复）")
        lines.append(f"- 内容问题: {len(self.content_issues)} 个")
        lines.append("")
        
        lines.append("## 格式问题详情")
        if self.format_issues:
            grouped = self._group_by_file(self.format_issues)
            for file, issues in sorted(grouped.items()):
                lines.append(f"  {file}:")
                for issue in issues:
                    lines.append(f"    - {issue.problem}")
                    if issue.suggestion:
                        lines.append(f"      {issue.suggestion}")
        else:
            lines.append("（无格式问题）")
        lines.append("")
        
        lines.append("## 结构问题详情")
        if self.structure_issues:
            grouped = self._group_by_file(self.structure_issues)
            for file, issues in sorted(grouped.items()):
                lines.append(f"  {file}:")
                for issue in issues:
                    lines.append(f"    - {issue.problem}")
                    if issue.suggestion:
                        lines.append(f"      {issue.suggestion}")
        else:
            lines.append("（无结构问题）")
        lines.append("")
        
        lines.append("## 内容问题详情")
        if self.content_issues:
            grouped = self._group_by_file(self.content_issues)
            for file, issues in sorted(grouped.items()):
                lines.append(f"  {file}:")
                for issue in issues:
                    lines.append(f"    - {issue.problem}")
                    if issue.suggestion:
                        lines.append(f"      {issue.suggestion}")
        else:
            lines.append("（无内容问题）")
        lines.append("")
        
        lines.append("## 下一步")
        if self.format_issues:
            lines.append('- 格式问题: 执行 "lint 并修复" 自动修复')
        if self.structure_issues:
            lines.append('- 结构问题: 执行 "lint 建议" 查看修复建议')
        if self.content_issues:
            lines.append('- 内容问题: 需人工判断处理')
        
        return "\n".join(lines)

    def _breakdown_by_problem(self, issues: List[Issue]) -> Dict[str, int]:
        breakdown = {}
        for issue in issues:
            breakdown[issue.problem] = breakdown.get(issue.problem, 0) + 1
        return breakdown

    def _group_by_file(self, issues: List[Issue]) -> Dict[str, List[Issue]]:
        grouped = {}
        for issue in issues:
            if issue.file not in grouped:
                grouped[issue.file] = []
            grouped[issue.file].append(issue)
        return grouped


def print_report(report: LintReport, mode: str = "summary"):
    if mode == "summary":
        print(report.summary())
    elif mode == "detailed":
        print(report.detailed())
    else:
        print(report.summary())


if __name__ == "__main__":
    report = LintReport()
    report.format_issues.append(Issue(
        category="格式",
        problem="缺失 source",
        file="entities/foo.md",
        suggestion="添加 source 字段"
    ))
    report.structure_issues.append(Issue(
        category="结构",
        problem="orphan page",
        file="entities/bar.md",
        suggestion="添加到 index.md"
    ))
    print(report.summary())
    print("\n" + "="*50 + "\n")
    print(report.detailed())