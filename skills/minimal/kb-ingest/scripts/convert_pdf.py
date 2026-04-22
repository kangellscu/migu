"""Convert PDF to markdown. Uses pdfplumber if available, falls back to placeholder."""

import sys
from pathlib import Path

def main(input_file: str, output_dir: str):
    src = Path(input_file)
    dst = Path(output_dir) / f"{src.stem}.md"
    dst.parent.mkdir(parents=True, exist_ok=True)

    try:
        import pdfplumber
        with pdfplumber.open(src) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        dst.write_text("\n\n".join(pages), encoding="utf-8")
        print(f"Converted: {src.name} -> {dst.name}")
    except ImportError:
        dst.write_text(
            f"# {src.stem}\n\n**PDF conversion pending**\n\n"
            f"Install pdfplumber: `pip install pdfplumber`\n\n"
            f"Raw PDF: `{src.name}`",
            encoding="utf-8",
        )
        print(f"Placeholder: {src.name} (install pdfplumber for full conversion)")
    except Exception as e:
        print(f"Error converting {src.name}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: convert_pdf.py <input.pdf> <output_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
