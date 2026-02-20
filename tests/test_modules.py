import pytest

from core.registry import get_registry
from core.models import PayloadTemplate, PayloadValidationError


# -----------------------------------------
# Setup
# -----------------------------------------

@pytest.fixture(scope="module")
def registry():
    return get_registry()


# -----------------------------------------
# XSS Tests
# -----------------------------------------

def test_xss_requires_context(registry):
    with pytest.raises(Exception):
        registry.generate("xss")  # context missing


def test_xss_html_generation(registry):
    items = registry.generate("xss", context="html")

    assert isinstance(items, list)
    assert len(items) > 0

    for item in items:
        assert isinstance(item, PayloadTemplate)
        assert item.module == "xss"
        assert item.context == "html"
        assert item.disabled_by_default is True
        assert "<<XSS_TEMPLATE" in item.payload
        assert item.risk_level in {"low", "medium", "high"}


# -----------------------------------------
# SQLi Tests
# -----------------------------------------

def test_sqli_requires_db(registry):
    with pytest.raises(Exception):
        registry.generate("sqli")


def test_sqli_mysql_generation(registry):
    items = registry.generate("sqli", db_type="mysql")

    assert len(items) > 0

    for item in items:
        assert item.module == "sqli"
        assert item.db_type == "mysql"
        assert "<<SQLI_TEMPLATE" in item.payload
        assert item.disabled_by_default is True


# -----------------------------------------
# CMD Tests
# -----------------------------------------

def test_cmd_requires_os(registry):
    with pytest.raises(Exception):
        registry.generate("cmd")


def test_cmd_linux_generation(registry):
    items = registry.generate("cmd", os_type="linux")

    assert len(items) > 0

    for item in items:
        assert item.module == "cmd"
        assert item.os_type == "linux"
        assert "<<CMD_TEMPLATE" in item.payload
        assert item.disabled_by_default is True


# -----------------------------------------
# Model Safety Enforcement
# -----------------------------------------

def test_disabled_flag_enforced(registry):
    items = registry.generate("xss", context="html")

    for item in items:
        assert item.disabled_by_default is True


def test_invalid_module(registry):
    with pytest.raises(Exception):
        registry.generate("invalid_module")
