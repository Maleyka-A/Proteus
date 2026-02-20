from __future__ import annotations

import base64
import binascii
import urllib.parse
from typing import Callable, Dict


class EncodingError(Exception):
    """Raised when encoding fails or invalid method is provided."""
    pass


# -----------------------------------------
# Encoding Implementations
# -----------------------------------------

def _url_encode(payload: str) -> str:
    return urllib.parse.quote(payload, safe="")


def _base64_encode(payload: str) -> str:
    encoded_bytes = base64.b64encode(payload.encode("utf-8", errors="strict"))
    return encoded_bytes.decode("ascii")


def _hex_encode(payload: str) -> str:
    return binascii.hexlify(
        payload.encode("utf-8", errors="strict")
    ).decode("ascii")


_ENCODING_METHODS: Dict[str, Callable[[str], str]] = {
    "url": _url_encode,
    "base64": _base64_encode,
    "hex": _hex_encode,
}


# -----------------------------------------
# Public API
# -----------------------------------------

def encode_payload(payload: str, *, method: str) -> str:
    """
    Encode payload TEMPLATE using selected method.

    Representation only. No execution.
    """

    # ---- Strict Validation ----

    if not isinstance(payload, str):
        raise EncodingError(
            f"Payload must be a string, got {type(payload)}."
        )

    if payload.strip() == "":
        raise EncodingError("Payload cannot be empty.")

    method_norm = (method or "").strip().lower()

    if method_norm not in _ENCODING_METHODS:
        raise EncodingError(
            f"Unsupported encoding method '{method}'. "
            f"Supported: {sorted(_ENCODING_METHODS.keys())}"
        )

    try:
        encoder = _ENCODING_METHODS[method_norm]
        return encoder(payload)

    except Exception as e:
        raise EncodingError(
            f"Encoding failed using method '{method_norm}': {e}"
        ) from e


def list_supported_encodings() -> list[str]:
    return sorted(_ENCODING_METHODS.keys())


def is_supported_encoding(method: str) -> bool:
    return (method or "").strip().lower() in _ENCODING_METHODS
