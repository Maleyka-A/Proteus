import json
from pathlib import Path

import pytest

from core.models import PayloadTemplate
from exporters.json_exporter import export_json, JSONExportError
from exporters.txt_exporter import export_txt, TXTExportError


# -------------------------------------------------
# Helper: create safe dummy payload
# -------------------------------------------------

def make_payload():
    return PayloadTemplate(
        module="xss",
        title="Test Payload",
        description="Test description",
        payload="<<XSS_TEMPLATE:TEST|CONTEXT=html|NON_EXECUTING>>",
        context="html",
        defensive_notes="Test notes",
        risk_level="low",
    )


# -------------------------------------------------
# JSON EXPORT TESTS
# -------------------------------------------------

def test_json_export_basic(tmp_path):
    items = [make_payload()]

    out_file = tmp_path / "out.json"
    export_json(items, out_file)

    assert out_file.exists()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert "schema" in data
    assert data["schema"] == "proteus.payloads.v1"
    assert data["count"] == 1
    assert len(data["payloads"]) == 1


def test_json_export_without_wrapper(tmp_path):
    items = [make_payload()]

    out_file = tmp_path / "out.json"
    export_json(items, out_file, include_wrapper=False)

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 1


def test_json_export_invalid_item(tmp_path):
    out_file = tmp_path / "out.json"

    with pytest.raises(JSONExportError):
        export_json([123], out_file)  # not PayloadTemplate


def test_json_export_disabled_flag_violation(tmp_path):
    bad = make_payload()
    bad.disabled_by_default = False  # violate safety

    out_file = tmp_path / "out.json"

    with pytest.raises(JSONExportError):
        export_json([bad], out_file)


# -------------------------------------------------
# TXT EXPORT TESTS
# -------------------------------------------------

def test_txt_export_basic(tmp_path):
    items = [make_payload()]

    out_file = tmp_path / "out.txt"
    export_txt(items, out_file)

    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8")

    assert "Proteus Payload Catalog" in content
    assert "Test Payload" in content
    assert "<<XSS_TEMPLATE" in content


def test_txt_export_invalid_item(tmp_path):
    out_file = tmp_path / "out.txt"

    with pytest.raises(TXTExportError):
        export_txt([123], out_file)


def test_txt_export_disabled_flag_violation(tmp_path):
    bad = make_payload()
    bad.disabled_by_default = False

    out_file = tmp_path / "out.txt"

    with pytest.raises(TXTExportError):
        export_txt([bad], out_file)
