"""Update compilation status in raw-registry.md using column name matching."""

import sys
from pathlib import Path
from datetime import datetime


def main(kb_dir: str, file_path: str, status: str):
    registry = Path(kb_dir) / "raw-registry.md"
    if not registry.exists():
        print("ERROR: raw-registry.md not found", file=sys.stderr)
        sys.exit(1)
    
    content = registry.read_text()
    lines = content.split("\n")
    today = datetime.now().strftime("%Y-%m-%d")
    
    header_line = None
    for i, line in enumerate(lines):
        if line.startswith("| 文件"):
            header_line = i
            break
    
    if header_line is None:
        print("ERROR: Header row not found", file=sys.stderr)
        sys.exit(1)
    
    header_cells = [c.strip() for c in lines[header_line].split("|")[1:-1]]
    
    try:
        compile_status_idx = header_cells.index("编译状态")
        last_processed_idx = header_cells.index("最近处理日期")
    except ValueError as e:
        print(f"ERROR: Column not found: {e}", file=sys.stderr)
        sys.exit(1)
    
    updated = False
    for i, line in enumerate(lines):
        if i <= header_line + 1:
            continue
        if file_path in line:
            cells = line.split("|")
            if len(cells) > max(compile_status_idx, last_processed_idx) + 1:
                cells[compile_status_idx + 1] = f" {status} "
                cells[last_processed_idx + 1] = f" {today} "
                lines[i] = "|".join(cells)
                updated = True
                break
    
    if updated:
        registry.write_text("\n".join(lines))
        print(f"Updated: {file_path} -> {status}")
    else:
        print(f"WARNING: Entry not found for {file_path}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: update_registry.py <kb_dir> <file_path> <status>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])