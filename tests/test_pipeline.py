from pathlib import Path

import pytest

from core.pipeline import run_pipeline, PipelineError


# ----------------------------
# Basic Generation
# ----------------------------

def test_pipeline_xss_html_generation():
    items = run_pipeline(
        module="xss",
        context="html",
    )

    assert len(items) > 0
    for item in items:
        assert item.module == "xss"
        assert item.context == "html"


def test_pipeline_sqli_mysql_generation():
    items = run_pipeline(
        module="sqli",
        db_type="mysql",
    )

    assert len(items) > 0
    for item in items:
        assert item.module == "sqli"
        assert item.db_type == "mysql"


def test_pipeline_cmd_linux_generation():
    items = run_pipeline(
        module="cmd",
        os_type="linux",
    )

    assert len(items) > 0
    for item in items:
        assert item.module == "cmd"
        assert item.os_type == "linux"


# ----------------------------
# Encoding / Obfuscation
# ----------------------------

def test_pipeline_with_encoding():
    items = run_pipeline(
        module="xss",
        context="html",
        encoding="base64",
    )

    assert len(items) > 0
    for item in items:
        assert "base64" in item.encoding_applied


def test_pipeline_with_obfuscation():
    items = run_pipeline(
        module="xss",
        context="html",
        obfuscation="mixed",   # supported mode
    )

    assert len(items) > 0
    for item in items:
        assert "mixed" in item.obfuscation_applied


# ----------------------------
# Export
# ----------------------------

def test_pipeline_json_export(tmp_path: Path):
    output_file = tmp_path / "out.json"

    items = run_pipeline(
        module="xss",
        context="html",
        export_format="json",
        output_path=str(output_file),
        meta={"test": "true"},
    )

    assert output_file.exists()
    assert len(items) > 0


def test_pipeline_txt_export(tmp_path: Path):
    output_file = tmp_path / "out.txt"

    items = run_pipeline(
        module="xss",
        context="html",
        export_format="txt",
        output_path=str(output_file),
    )

    assert output_file.exists()
    assert len(items) > 0


# ----------------------------
# Error Handling
# ----------------------------

def test_pipeline_missing_required_selector():
    with pytest.raises(PipelineError):
        run_pipeline(module="sqli")  # db_type required


def test_pipeline_invalid_module():
    with pytest.raises(PipelineError):
        run_pipeline(module="invalid")
