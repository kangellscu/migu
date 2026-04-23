# tests/skills/test_kb_ingest.py
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "minimal"
SCRIPTS = SKILLS_DIR / "kb-ingest" / "scripts"

def test_scan_raw(tmp_path):
    """Verify scan_raw.py detects files."""
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "test.md").write_text("# test")
    (raw / "doc.pdf").write_bytes(b"%PDF-fake")
    ext = raw / ".extracted"
    ext.mkdir()
    (ext / "old.md").write_text("# old")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "scan_raw.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "test.md|markdown" in result.stdout
    assert "doc.pdf|pdf" in result.stdout
    assert "old.md" not in result.stdout

def test_scan_raw_missing(tmp_path):
    """Verify scan_raw.py errors on missing raw/."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "scan_raw.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "raw/ directory not found" in result.stderr

def test_normalize_markdown(tmp_path):
    """Verify normalize_markdown.py copies and fixes content."""
    src = tmp_path / "src.md"
    dst = tmp_path / "dst.md"
    src.write_text("# Hello\n\nSome content.")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "normalize_markdown.py"), str(src), str(dst)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert dst.exists()
    assert dst.read_text() == "# Hello\n\nSome content."

def test_convert_pdf_placeholder(tmp_path):
    """Verify convert_pdf.py creates placeholder when pdfplumber missing."""
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"fake-pdf")
    output = tmp_path / "out"
    output.mkdir()
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "convert_pdf.py"), str(pdf), str(output)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert (output / "test.md").exists()

def test_validate_batch_valid(tmp_path):
    """Verify validate_batch.py passes on valid registry."""
    registry = tmp_path / "raw-registry.md"
    registry.write_text("""| 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
|------|------|------|-----------|---------|---------|-------------|
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "validate_batch.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "VALID" in result.stdout

def test_normalize_cjk_radical(tmp_path):
    """CJK radical converts to unified ideograph."""
    input_file = tmp_path / "test.md"
    output_file = tmp_path / "output.md"
    
    # Kangxi RADICAL ONE (U+2F00) + normal char
    content = "\u2f00\u4e00\u4e28"
    input_file.write_text(content, encoding="utf-8")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "normalize_markdown.py"),
         str(input_file), str(output_file)],
        capture_output=True,
    )
    
    assert result.returncode == 0
    output = output_file.read_text(encoding="utf-8")
    assert "\u2f00" not in output
    assert output == "\u4e00\u4e00\u4e28"

def test_normalize_cjk_radical_multiple(tmp_path):
    """Multiple CJK radicals convert correctly."""
    input_file = tmp_path / "test.md"
    output_file = tmp_path / "output.md"
    
    # Mix of CJK Radicals Supplement + Kangxi + Strokes + normal chars
    content = "\u2e85\u2f08\u31d0\u4e00\u4eba"
    input_file.write_text(content, encoding="utf-8")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "normalize_markdown.py"),
         str(input_file), str(output_file)],
        capture_output=True,
    )
    
    assert result.returncode == 0
    output = output_file.read_text(encoding="utf-8")
    assert "\u2e85" not in output
    assert "\u2f08" not in output
    assert "\u31d0" not in output
    assert output == "\u4ebb\u4eba\u4e00\u4e00\u4eba"

def test_normalize_preserves_normal_chars(tmp_path):
    """Normal Chinese characters are unchanged."""
    input_file = tmp_path / "test.md"
    output_file = tmp_path / "output.md"
    
    content = "刘邦项羽张良韩信"
    input_file.write_text(content, encoding="utf-8")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "normalize_markdown.py"),
         str(input_file), str(output_file)],
        capture_output=True,
    )
    
    assert result.returncode == 0
    output = output_file.read_text(encoding="utf-8")
    assert output == content
