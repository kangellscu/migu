"""Format dashboard output from registry and index stats."""

import sys

def main():
    lines = sys.stdin.read().strip().split("\n")
    
    kb_dir = ""
    raw_total = 0
    raw_types = {}
    pending_ingest = 0
    pending_compile = 0
    pending_files = []
    wiki_total = 0
    wiki_sections = {}
    
    for line in lines:
        if line.startswith("kb_dir:"):
            kb_dir = line.split(":", 1)[1]
        elif line.startswith("raw_total:"):
            raw_total = int(line.split(":", 1)[1])
        elif line.startswith("raw_types:"):
            for pair in line.split(":", 1)[1].split(","):
                if ":" in pair:
                    k, v = pair.split(":")
                    raw_types[k] = int(v)
        elif line.startswith("pending_ingest:"):
            pending_ingest = int(line.split(":", 1)[1])
        elif line.startswith("pending_compile:"):
            pending_compile = int(line.split(":", 1)[1])
        elif line.startswith("pending:"):
            pending_files.append(line.split(":", 1)[1])
        elif line.startswith("wiki_total:"):
            wiki_total = int(line.split(":", 1)[1])
        elif line.startswith("wiki_sections:"):
            for pair in line.split(":", 1)[1].split(","):
                if ":" in pair:
                    k, v = pair.split(":")
                    wiki_sections[k] = int(v)
    
    name = kb_dir.split("/")[-1] if kb_dir else "unknown"
    type_parts = ", ".join(f"{k}: {v}" for k, v in raw_types.items()) if raw_types else "none"
    section_parts = ", ".join(f"{k}: {v}" for k, v in wiki_sections.items()) if wiki_sections else "none"
    
    print(f"Knowledge Base Dashboard: {name}/")
    print()
    print("┌─────────────────────────────────────────────────┐")
    print("│ Overview                                         │")
    print("├─────────────────────────────────────────────────┤")
    print(f"│ Raw Files:         {raw_total} ({type_parts})")
    print(f"│ Wiki Documents:    {wiki_total} ({section_parts})")
    print(f"│ Pending Ingest:    {pending_ingest} files")
    print(f"│ Pending Compile:   {pending_compile} files")
    print("└─────────────────────────────────────────────────┘")
    
    if pending_ingest == 0 and pending_compile == 0:
        print()
        print("┌─────────────────────────────────────────────────┐")
        print("│ Status                                            │")
        print("├─────────────────────────────────────────────────┤")
        print("│ All up to date                                    │")
        print("└─────────────────────────────────────────────────┘")
    
    if pending_files:
        print()
        print("┌─────────────────────────────────────────────────┐")
        print("│ Pending Files                                     │")
        print("├─────────────────────────────────────────────────┤")
        for pf in pending_files[:10]:
            parts = pf.split("|")
            if len(parts) >= 3:
                print(f"│ {parts[0]:40s} ({parts[1]}, {parts[2]}) │")
        if len(pending_files) > 10:
            print(f"│ ... ({len(pending_files) - 10} more)")
        print("└─────────────────────────────────────────────────┘")

if __name__ == "__main__":
    main()
