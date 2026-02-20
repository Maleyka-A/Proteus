import pytest

from transforms.encoder import (
    encode_payload,
    list_supported_encodings,
    is_supported_encoding,
    EncodingError,
)


# -----------------------------------------
# Supported methods
# -----------------------------------------

def test_list_supported_encodings():
    methods = list_supported_encodings()
    assert isinstance(methods, list)
    assert "url" in methods
    assert "base64" in methods
    assert "hex" in methods


def test_is_supported_encoding():
    assert is_supported_encoding("url") is True
    assert is_supported_encoding("BASE64") is True
    assert is_supported_encoding("invalid") is False


# -----------------------------------------
# URL Encoding
# -----------------------------------------

def test_url_encoding():
    payload = "TEST TEMPLATE"
    encoded = encode_payload(payload, method="url")
    assert encoded == "TEST%20TEMPLATE"


# -----------------------------------------
# Base64 Encoding
# -----------------------------------------

def test_base64_encoding():
    payload = "TEST"
    encoded = encode_payload(payload, method="base64")
    assert encoded == "VEVTVA=="


# -----------------------------------------
# Hex Encoding
# -----------------------------------------

def test_hex_encoding():
    payload = "TEST"
    encoded = encode_payload(payload, method="hex")
    assert encoded == "54455354"


# -----------------------------------------
# Invalid method
# -----------------------------------------

def test_invalid_encoding_method():
    with pytest.raises(EncodingError):
        encode_payload("TEST", method="invalid")


# -----------------------------------------
# Empty payload
# -----------------------------------------

def test_empty_payload():
    with pytest.raises(EncodingError):
        encode_payload("", method="url")


# -----------------------------------------
# Non-string payload
# -----------------------------------------

def test_non_string_payload():
    with pytest.raises(EncodingError):
        encode_payload(123, method="url")  # type: ignore
