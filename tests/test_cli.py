from pathlib import Path
import pytest

from cli import main as cli_main


# ----------------------------
# Preview Mode
# ----------------------------

def test_cli_generate_xss_preview():
    exit_code = cli_main([
        "generate",
        "--module", "xss",
        "--context", "html",
    ])

    assert exit_code == 0


def test_cli_generate_sqli_preview():
    exit_code = cli_main([
        "generate",
        "--module", "sqli",
        "--db", "mysql",
    ])

    assert exit_code == 0


# ----------------------------
# JSON Export
# ----------------------------

def test_cli_json_export(tmp_path: Path):
    output_file = tmp_path / "cli_out.json"

    exit_code = cli_main([
        "generate",
        "--module", "xss",
        "--context", "html",
        "--export", "json",
        "--output", str(output_file),
    ])

    assert exit_code == 0
    assert output_file.exists()


# ----------------------------
# TXT Export
# ----------------------------

def test_cli_txt_export(tmp_path: Path):
    output_file = tmp_path / "cli_out.txt"

    exit_code = cli_main([
        "generate",
        "--module", "xss",
        "--context", "html",
        "--export", "txt",
        "--output", str(output_file),
    ])

    assert exit_code == 0
    assert output_file.exists()


# ----------------------------
# Errors
# ----------------------------

def test_cli_missing_selector():
    exit_code = cli_main([
        "generate",
        "--module", "sqli",
    ])

    assert exit_code == 1


def test_cli_invalid_module():
    with pytest.raises(SystemExit):
        cli_main([
            "generate",
            "--module", "invalid",
        ])
