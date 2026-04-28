"""Update raw-registry.md with file processing status.

Usage:
    update_registry.py <kb_dir> --file <path> --type <type> --status <status> [--output <path>]

Or batch mode via stdin JSON:
    update_registry.py <kb_dir> --batch
    (reads JSON lines: {"file": "...", "type": "...", "status": "...", "output_path": "..."})
"""

import json
import re
import sys
from datetime import date
from pathlib import Path


def normalize_path(path: str) -> str:
    """Remove wikilink format and extract clean path.
    
    Examples:
        "[[raw/史记/本纪/秦本纪.md]]" -> "史记/本纪/秦本纪.md"
        "[[raw/.extracted/史记/本纪/秦本纪.md]]" -> ".extracted/史记/本纪/秦本纪.md"
        "史记/本纪/秦本纪.md" -> "史记/本纪/秦本纪.md"
    """
    if path.startswith('[[') and path.endswith(']]'):
        path = path[2:-2]
        if path.startswith('raw/'):
            path = path[4:]
    return path


def parse_registry(content: str) -> tuple[list[str], list[dict]]:
    """Parse raw-registry.md into header lines and entries."""
    lines = content.split('\n')
    header_lines = []
    entries = []
    in_table = False
    
    for line in lines:
        if line.startswith('| File |'):
            in_table = True
            header_lines.append(line)
        elif line.startswith('|------|'):
            header_lines.append(line)
        elif in_table and line.startswith('|') and not line.startswith('|------|'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 9 and parts[1]:  # Has file path
                entries.append({
                    'file': parts[1],
                    'type': parts[2],
                    'summary': parts[3],
                    'preprocess_status': parts[4],
                    'product_path': parts[5],
                    'compile_status': parts[6],
                    'last_processed': parts[7],
                    'remaining_omissions': parts[8]
                })
        elif in_table and not line.startswith('|'):
            in_table = False
            header_lines.append(line)
        else:
            header_lines.append(line)
    
    return header_lines, entries


def format_entry(entry: dict) -> str:
    """Format entry as table row."""
    return f"| {entry['file']} | {entry['type']} | {entry['summary']} | {entry['preprocess_status']} | {entry['product_path']} | {entry['compile_status']} | {entry['last_processed']} | {entry['remaining_omissions']} |"


def update_registry(kb_dir: Path, file_path: str, file_type: str, 
                    status: str, output_path: str | None):
    """Update or add entry in raw-registry.md."""
    registry_file = kb_dir / "raw-registry.md"
    
    if not registry_file.exists():
        print(f"ERROR: raw-registry.md not found at {registry_file}", file=sys.stderr)
        sys.exit(1)
    
    content = registry_file.read_text(encoding='utf-8')
    header_lines, entries = parse_registry(content)
    
    today = str(date.today())
    
    found = False
    for entry in entries:
        if normalize_path(entry['file']) == file_path:
            entry['file'] = file_path
            entry['type'] = file_type
            entry['preprocess_status'] = '已处理' if status == 'processed' else '无需处理'
            entry['product_path'] = output_path if output_path else '-'
            entry['last_processed'] = today
            found = True
            break
    
    if not found:
        entries.append({
            'file': file_path,
            'type': file_type,
            'summary': '',
            'preprocess_status': '已处理' if status == 'processed' else '无需处理',
            'product_path': output_path if output_path else '-',
            'compile_status': '-',
            'last_processed': today,
            'remaining_omissions': '-'
        })
    
    new_lines = header_lines.copy()
    table_start = None
    for i, line in enumerate(new_lines):
        if line.startswith('| File |'):
            table_start = i
            break
    
    if table_start is not None:
        new_lines = new_lines[:table_start + 2]  # Keep header and separator
        for entry in entries:
            new_lines.append(format_entry(entry))
        
        remaining_lines = header_lines[table_start + 2:]
        for entry in entries[:table_start + 2]:
            remaining_lines = remaining_lines[len(entries):]
        new_lines.extend(remaining_lines)
    
    registry_file.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
    print(f"Updated: {file_path} -> {status}")


def main():
    if len(sys.argv) < 2:
        print("Usage: update_registry.py <kb_dir> --file <path> --type <type> --status <status> [--output <path>]", file=sys.stderr)
        print("Or: update_registry.py <kb_dir> --batch (reads JSON from stdin)", file=sys.stderr)
        sys.exit(1)
    
    kb_dir = Path(sys.argv[1])
    
    if '--batch' in sys.argv:
        for line in sys.stdin:
            if line.strip():
                data = json.loads(line)
                update_registry(
                    kb_dir,
                    data['file'],
                    data.get('type', 'markdown'),
                    data['status'],
                    data.get('output_path')
                )
    else:
        args = sys.argv[2:]
        file_path = None
        file_type = 'markdown'
        status = None
        output_path = None
        
        i = 0
        while i < len(args):
            if args[i] == '--file' and i + 1 < len(args):
                file_path = args[i + 1]
                i += 2
            elif args[i] == '--type' and i + 1 < len(args):
                file_type = args[i + 1]
                i += 2
            elif args[i] == '--status' and i + 1 < len(args):
                status = args[i + 1]
                i += 2
            elif args[i] == '--output' and i + 1 < len(args):
                output_path = args[i + 1]
                i += 2
            else:
                i += 1
        
        if not file_path or not status:
            print("ERROR: --file and --status required", file=sys.stderr)
            sys.exit(1)
        
        update_registry(kb_dir, file_path, file_type, status, output_path)


if __name__ == "__main__":
    main()