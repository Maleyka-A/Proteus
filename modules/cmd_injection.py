from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Sequence

from core.models import PayloadTemplate
from core.registry import registry

OSType = Literal["linux", "windows"]

# -----------------------------------------
# OS Normalization (with aliases)
# -----------------------------------------

_VALID_OS_TYPES: Dict[str, OSType] = {
    # Linux bucket
    "linux": "linux",
    "unix": "linux",
    "gnu/linux": "linux",
    "bash": "linux",
    "sh": "linux",

    # Windows bucket
    "windows": "windows",
    "win": "windows",
    "win32": "windows",
    "cmd": "windows",
    "powershell": "windows",
    "pwsh": "windows",
}


def _normalize_os(os_type: str) -> OSType:
    raw = (os_type or "").strip().lower()
    os_norm = _VALID_OS_TYPES.get(raw)
    if not os_norm:
        supported = sorted(set(_VALID_OS_TYPES.values()))
        raise ValueError(
            f"Invalid os_type '{os_type}'. Supported: {supported}"
        )
    return os_norm


# -----------------------------------------
# OS-Specific Defensive Notes
# -----------------------------------------

def _os_defense_highlights(os_type: OSType) -> str:
    if os_type == "linux":
        return (
            "- Avoid shell=True patterns in process spawning.\n"
            "- Prefer exec-style APIs with argument arrays (argv).\n"
            "- Apply strict allow-lists for user-controlled parameters.\n"
        )

    return (
        "- Avoid passing untrusted input into cmd.exe or PowerShell.\n"
        "- Prefer structured APIs instead of dynamic command construction.\n"
        "- Restrict privileges and monitor spawned processes.\n"
    )


# -----------------------------------------
# Template Specification
# -----------------------------------------

@dataclass(frozen=True)
class _TemplateSpec:
    key: str
    title: str
    risk: Literal["low", "medium", "high"]
    tags: Sequence[str]
    description: str
    defensive_notes: str


_TEMPLATES: Sequence[_TemplateSpec] = (
    _TemplateSpec(
        key="BASIC_CONCEPT",
        title="Command Injection (Basic Concept)",
        risk="high",
        tags=("cmd-injection", "basic-concept", "education-only", "non-executing"),
        description=(
            "Concept: untrusted input influencing system command construction "
            "may alter execution flow."
        ),
        defensive_notes=(
            "- Root cause: concatenating user input into shell commands.\n"
            "- Primary defense: avoid shell invocation entirely.\n"
        ),
    ),
    _TemplateSpec(
        key="SEPARATOR_CONCEPT",
        title="Command Separator Concept",
        risk="high",
        tags=("cmd-injection", "separator-concept", "education-only", "non-executing"),
        description=(
            "Concept: shell parsing rules may interpret separators as command boundaries."
        ),
        defensive_notes=(
            "- Do not rely on character blacklists.\n"
            "- Use structured execution (argv arrays), not shell parsing.\n"
        ),
    ),
    _TemplateSpec(
        key="CHAINING_CONCEPT",
        title="Command Chaining Concept",
        risk="high",
        tags=("cmd-injection", "chaining-concept", "education-only", "non-executing"),
        description=(
            "Concept: dynamic command building may enable chained execution paths."
        ),
        defensive_notes=(
            "- Avoid dynamic command construction.\n"
            "- Enforce strict input validation.\n"
        ),
    ),
    _TemplateSpec(
        key="FILTER_EVASION_CONCEPTS",
        title="Filter Evasion Concepts",
        risk="medium",
        tags=("cmd-injection", "bypass-concepts", "education-only", "non-executing"),
        description=(
            "Concept: naive filtering may fail across encodings and shell behaviors."
        ),
        defensive_notes=(
            "- Architectural prevention > keyword filtering.\n"
            "- Add sandboxing and least privilege.\n"
        ),
    ),
    _TemplateSpec(
        key="OS_DETECTION_LOGIC",
        title="OS Detection Logic Concept",
        risk="low",
        tags=("cmd-injection", "os-detection", "education-only", "non-executing"),
        description=(
            "Concept: behavioral differences may reveal underlying OS type."
        ),
        defensive_notes=(
            "- Avoid exposing platform details.\n"
            "- Do not return raw command output.\n"
        ),
    ),
)


# -----------------------------------------
# Generator
# -----------------------------------------

@registry.register_module("cmd", requires_os=True)
def generate_payloads(*, os_type: str) -> List[PayloadTemplate]:

    os_norm = _normalize_os(os_type)

    os_tag = f"os:{os_norm}"
    os_specific_notes = _os_defense_highlights(os_norm)

    items: List[PayloadTemplate] = []

    for spec in _TEMPLATES:

        marker = (
            f"<<CMD_TEMPLATE: {spec.key} | "
            f"OS={os_norm} | NON_EXECUTING>>"
        )

        combined_notes = (
            "Education-only (non-executing).\n"
            f"{spec.defensive_notes}"
            f"{os_specific_notes}"
            "- Apply least privilege to service accounts.\n"
            "- Prefer SDK/library APIs over invoking shell utilities.\n"
        )

        items.append(
            PayloadTemplate(
                module="cmd",
                title=f"{spec.title} ({os_norm}) - Template",
                description=spec.description,
                payload=marker,
                os_type=os_norm,
                defensive_notes=combined_notes,
                risk_level=spec.risk,
                tags=[*spec.tags, os_tag],
            )
        )

    return items
