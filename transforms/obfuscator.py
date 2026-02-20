from __future__ import annotations

import re
from typing import Callable, Dict


# ------------------------------
# Exceptions
# ------------------------------

class ObfuscationError(Exception):
    """Raised when obfuscation fails or invalid mode is provided."""
    pass


# ------------------------------
# Safety guard (education-only)
# ------------------------------
# Only allow obfuscation for explicit educational templates.
# This helps prevent accidentally transforming "real" payload strings.
_TEMPLATE_MARKER_RE = re.compile(r"(<<.*?>>)|(\bTEMPLATE\b)", re.IGNORECASE)


def _ensure_educational_template(payload: str) -> None:
    if not _TEMPLATE_MARKER_RE.search(payload or ""):
        raise ObfuscationError(
            "Refusing to obfuscate: payload does not look like an educational template. "
            "Add a marker like '<<...>>' or the word 'TEMPLATE'."
        )


# ------------------------------
# Obfuscation Implementations (representation-only)
# ------------------------------

def _comments(payload: str) -> str:
    """
    Comment insertion (representation-only).

    Inserts a neutral marker '/*OBF*/' at controlled points to demonstrate
    how comment tokens can change signatures in filters.
    """
    _ensure_educational_template(payload)

    out = []
    for ch in payload:
        out.append(ch)
        # Insert marker occasionally after alphanumerics (deterministic pattern)
        if ch.isalnum() and (ord(ch) % 7 == 0):
            out.append("/*OBF*/")
    return "".join(out)


def _whitespace(payload: str) -> str:
    """
    Whitespace abuse (representation-only).

    Replaces normal spaces with a mixed whitespace sequence to demonstrate
    parsing differences. This is purely textual.
    """
    _ensure_educational_template(payload)

    # Replace each single space with a fixed mixed sequence (deterministic & simple)
    return payload.replace(" ", " \t ")


def _mixed(payload: str) -> str:
    """
    Mixed obfuscation: comments + whitespace.
    """
    _ensure_educational_template(payload)
    return _whitespace(_comments(payload))


# ------------------------------
# Registry of Supported Modes
# (Aligned with CLI choices: comments/whitespace/mixed)
# ------------------------------

_OBFUSCATION_MODES: Dict[str, Callable[[str], str]] = {
    "comments": _comments,
    "whitespace": _whitespace,
    "mixed": _mixed,
}


# ------------------------------
# Public API
# ------------------------------

def obfuscate_payload(payload: str, *, mode: str) -> str:
    """
    Apply educational obfuscation technique to payload TEMPLATE.

    Supported modes:
        - comments
        - whitespace
        - mixed

    Representation only. No execution, no evaluation.
    """
    if not isinstance(payload, str):
        raise ObfuscationError(f"Payload must be a string, got {type(payload)}.")
    if payload == "":
        raise ObfuscationError("Payload cannot be empty.")

    mode_norm = (mode or "").strip().lower()
    if mode_norm not in _OBFUSCATION_MODES:
        raise ObfuscationError(
            f"Unsupported obfuscation mode '{mode}'. "
            f"Supported: {sorted(_OBFUSCATION_MODES.keys())}"
        )

    try:
        transformer = _OBFUSCATION_MODES[mode_norm]
        return transformer(payload)
    except ObfuscationError:
        raise
    except Exception as e:
        raise ObfuscationError(f"Obfuscation failed using mode '{mode_norm}': {e}") from e


def list_supported_obfuscations() -> list[str]:
    """Return list of available obfuscation modes (for CLI help)."""
    return sorted(_OBFUSCATION_MODES.keys())


def is_supported_obfuscation(mode: str) -> bool:
    """Quick validation helper for CLI layer."""
    return (mode or "").strip().lower() in _OBFUSCATION_MODES
