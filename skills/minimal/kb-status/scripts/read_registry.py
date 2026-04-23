"""Parse raw-registry.md and return statistics."""

import sys
from pathlib import Path

def main(kb_dir: str):
    registry_file = Path(kb_dir) / "raw-registry.md"
    if not registry_file.exists():
        print("ERROR: raw-registry.md not found", file=sys.stderr)
        sys.exit(1)
    
    content = registry_file.read_text()
    lines = content.strip().split("\n")
    
    data_lines = []
    in_table = False
    for line in lines:
        if line.startswith("|") and ("---" in line or "------" in line):
            in_table = True
            continue
        if in_table and line.strip():
            data_lines.append(line)
    
    entries = []
    for line in data_lines:
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) >= 7:
            entries.append({
                "file": cells[0],
                "type": cells[1],
                "summary": cells[2],
                "preprocess_status": cells[3],
                "product_path": cells[4],
                "compile_status": cells[5],
                "last_processed": cells[6],
            })
    
    type_counts = {}
    status_counts = {"未处理": 0, "已处理": 0, "无需处理": 0}
    compile_counts = {"未编译": 0, "已编译": 0, "部分编译": 0, "已引用": 0, "": 0}
    
    for entry in entries:
        t = entry["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
        ps = entry["preprocess_status"]
        if ps in status_counts:
            status_counts[ps] += 1
        cs = entry["compile_status"]
        if cs in compile_counts:
            compile_counts[cs] += 1
    
    pending_ingest = status_counts["未处理"]
    pending_compile = compile_counts["未编译"] + compile_counts["部分编译"]
    
    print(f"total:{len(entries)}")
    print(f"types:{','.join(f'{k}:{v}' for k, v in type_counts.items())}")
    print(f"pending_ingest:{pending_ingest}")
    print(f"pending_compile:{pending_compile}")
    for entry in entries:
        if entry["preprocess_status"] == "未处理" or entry["compile_status"] in ("未编译", "部分编译"):
            print(f"pending:{entry['file']}|{entry['preprocess_status']}|{entry['compile_status']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: read_registry.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
