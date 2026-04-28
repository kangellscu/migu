"""Tests for normalize_markdown.py output logic."""

import json
import subprocess
import tempfile
from pathlib import Path


def test_no_bom_no_radicals_returns_skipped():
    """文件无 BOM 无康熙部首，返回 skipped 状态，不创建产物。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_dir = Path(tmpdir) / "raw"
        raw_dir.mkdir()
        
        src_file = raw_dir / "test.md"
        src_file.write_text("正常内容", encoding="utf-8")
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/normalize_markdown.py",
             str(src_file), str(raw_dir)],
            capture_output=True,
            text=True,
            cwd="/Users/23mofang/Documents/knowledge-bases/migu"
        )
        
        output = json.loads(result.stdout)
        assert output["status"] == "skipped"
        assert output["output_path"] is None
        assert output["issues"] == []
        
        extracted_dir = raw_dir / ".extracted"
        assert not extracted_dir.exists()


def test_bom_only_returns_processed():
    """文件有 BOM，返回 processed 状态，创建产物。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_dir = Path(tmpdir) / "raw"
        raw_dir.mkdir()
        
        src_file = raw_dir / "test.md"
        src_file.write_text("\ufeff有BOM内容", encoding="utf-8")
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/normalize_markdown.py",
             str(src_file), str(raw_dir)],
            capture_output=True,
            text=True,
            cwd="/Users/23mofang/Documents/knowledge-bases/migu"
        )
        
        output = json.loads(result.stdout)
        assert output["status"] == "processed"
        assert output["output_path"] == ".extracted/test.md"
        assert output["issues"] == ["bom"]
        
        extracted_file = raw_dir / ".extracted" / "test.md"
        assert extracted_file.exists()
        content = extracted_file.read_text(encoding="utf-8")
        assert not content.startswith("\ufeff")


def test_radicals_only_returns_processed():
    """文件有康熙部首，返回 processed 状态，创建产物。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_dir = Path(tmpdir) / "raw"
        raw_dir.mkdir()
        
        src_file = raw_dir / "test.md"
        src_file.write_text("康熙部首⼈", encoding="utf-8")
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/normalize_markdown.py",
             str(src_file), str(raw_dir)],
            capture_output=True,
            text=True,
            cwd="/Users/23mofang/Documents/knowledge-bases/migu"
        )
        
        output = json.loads(result.stdout)
        assert output["status"] == "processed"
        assert output["output_path"] == ".extracted/test.md"
        assert output["issues"] == ["radicals"]
        
        extracted_file = raw_dir / ".extracted" / "test.md"
        assert extracted_file.exists()
        content = extracted_file.read_text(encoding="utf-8")
        assert content == "康熙部首人"


def test_both_bom_and_radicals_returns_processed():
    """文件有 BOM 和康熙部首，返回 processed 状态，issues 包含两者。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_dir = Path(tmpdir) / "raw"
        raw_dir.mkdir()
        
        src_file = raw_dir / "test.md"
        src_file.write_text("\ufeff康熙部首⼈", encoding="utf-8")
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/normalize_markdown.py",
             str(src_file), str(raw_dir)],
            capture_output=True,
            text=True,
            cwd="/Users/23mofang/Documents/knowledge-bases/migu"
        )
        
        output = json.loads(result.stdout)
        assert output["status"] == "processed"
        assert output["output_path"] == ".extracted/test.md"
        assert "bom" in output["issues"]
        assert "radicals" in output["issues"]