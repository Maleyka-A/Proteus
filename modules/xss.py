from __future__ import annotations

from typing import List, Optional

from core.models import PayloadTemplate
from core.registry import registry


_VALID_CONTEXTS = {"html", "attr", "js"}


def _normalize_context(context: Optional[str]) -> Optional[str]:
    if context is None:
        return None
    c = (context or "").strip().lower()
    if c == "":
        return None
    if c not in _VALID_CONTEXTS:
        raise ValueError(f"Invalid XSS context '{context}'. Supported: {sorted(_VALID_CONTEXTS)}")
    return c


@registry.register_module("xss")
def generate_payloads(*, context: Optional[str] = None) -> List[PayloadTemplate]:
    """
    Educational XSS template generator (NON-EXECUTING).

    Generates inert template markers that demonstrate:
      - Reflected XSS concept
      - Stored XSS concept
      - DOM-based XSS concept
      - Context awareness: HTML / Attribute / JavaScript

    Notes:
    - Templates contain explicit markers (<<...>>) to remain education-only.
    - No real exploit payloads are generated.
    """
    ctx = _normalize_context(context)

    items: List[PayloadTemplate] = []

    # --------------------------
    # HTML context templates
    # --------------------------
    if ctx in (None, "html"):
        items.extend(
            [
                PayloadTemplate(
                    module="xss",
                    title="Reflected XSS (HTML context) - Template",
                    description=(
                        "Demonstrates reflected XSS risk when untrusted input is placed into the HTML body "
                        "without proper contextual output encoding."
                    ),
                    payload="<<XSS_TEMPLATE: REFLECTED | CONTEXT=html | SINK=HTML_BODY>>",
                    context="html",
                    defensive_notes=(
                        "Education-only template (non-executing).\n"
                        "- Root cause: reflecting user input into HTML without encoding.\n"
                        "- Defenses: contextual output encoding (HTML), safe templating/auto-escaping, CSP.\n"
                        "- WAFs may detect signatures, but correct output encoding is the core fix."
                    ),
                    risk_level="medium",
                    tags=["reflected", "context:html", "education-only", "non-executing"],
                ),
                PayloadTemplate(
                    module="xss",
                    title="Stored XSS (HTML context) - Template",
                    description=(
                        "Demonstrates stored XSS concept: input is persisted and later rendered into HTML body."
                    ),
                    payload="<<XSS_TEMPLATE: STORED | CONTEXT=html | SOURCE=persisted_input | SINK=HTML_BODY>>",
                    context="html",
                    defensive_notes=(
                        "Education-only template (non-executing).\n"
                        "- Stored XSS can affect many users because the payload is persisted.\n"
                        "- Defenses: encode at render time, input normalization/validation, CSP.\n"
                        "- Ensure consistent escaping across all render paths."
                    ),
                    risk_level="high",
                    tags=["stored", "context:html", "education-only", "non-executing"],
                ),
            ]
        )

    # --------------------------
    # Attribute context templates
    # --------------------------
    if ctx in (None, "attr"):
        items.extend(
            [
                PayloadTemplate(
                    module="xss",
                    title="Reflected XSS (Attribute context) - Template",
                    description=(
                        "Demonstrates attribute-context injection risk when input is placed into an HTML attribute "
                        "value without proper attribute encoding/validation."
                    ),
                    payload="<<XSS_TEMPLATE: REFLECTED | CONTEXT=attr | SINK=ATTRIBUTE_VALUE>>",
                    context="attr",
                    defensive_notes=(
                        "Education-only template (non-executing).\n"
                        "- Attribute context requires attribute-safe encoding (quotes/special chars).\n"
                        "- For URL attributes (href/src), apply allow-list validation for schemes/protocols.\n"
                        "- Avoid event-handler attributes entirely; prefer safe DOM APIs."
                    ),
                    risk_level="medium",
                    tags=["reflected", "context:attr", "education-only", "non-executing"],
                ),
                PayloadTemplate(
                    module="xss",
                    title="Stored XSS (Attribute context) - Template",
                    description=(
                        "Demonstrates stored XSS concept where persisted input is later used inside an HTML attribute."
                    ),
                    payload="<<XSS_TEMPLATE: STORED | CONTEXT=attr | SOURCE=persisted_input | SINK=ATTRIBUTE_VALUE>>",
                    context="attr",
                    defensive_notes=(
                        "Education-only template (non-executing).\n"
                        "- Stored attribute injection can be severe depending on sink type.\n"
                        "- Defenses: strict allow-lists + attribute encoding; avoid dangerous attribute sinks.\n"
                        "- Prefer framework auto-escaping and safe URL builders."
                    ),
                    risk_level="high",
                    tags=["stored", "context:attr", "education-only", "non-executing"],
                ),
                PayloadTemplate(
                    module="xss",
                    title="Filter Evasion Concepts (Attribute context) - Template",
                    description=(
                        "Marker template for discussing why naive filters fail in attribute context "
                        "(context switching, encoding differences) without providing operational exploit strings."
                    ),
                    payload="<<XSS_TEMPLATE: BYPASS_CONCEPTS | CONTEXT=attr | NOTE=descriptive_only>>",
                    context="attr",
                    defensive_notes=(
                        "Education-only template (non-executing).\n"
                        "- Naive filters often match strings; robust defense is context-aware output encoding.\n"
                        "- Use allow-lists for URL schemes and avoid inline event handlers.\n"
                        "- CSP can reduce impact, but correct encoding is primary."
                    ),
                    risk_level="low",
                    tags=["bypass-concepts", "context:attr", "education-only", "non-executing"],
                ),
            ]
        )

    # --------------------------
    # JavaScript context templates
    # --------------------------
    if ctx in (None, "js"):
        items.extend(
            [
                PayloadTemplate(
                    module="xss",
                    title="Reflected XSS (JavaScript context) - Template",
                    description=(
                        "Demonstrates risk when untrusted input is embedded into a JavaScript string/context "
                        "without proper JS escaping."
                    ),
                    payload="<<XSS_TEMPLATE: REFLECTED | CONTEXT=js | SINK=JS_STRING>>",
                    context="js",
                    defensive_notes=(
                        "Education-only template (non-executing).\n"
                        "- JS context needs JS-string escaping (different from HTML/attr).\n"
                        "- Avoid string concatenation; prefer safe APIs and JSON encoding.\n"
                        "- CSP helps, but correct contextual escaping is essential."
                    ),
                    risk_level="high",
                    tags=["reflected", "context:js", "education-only", "non-executing"],
                ),
                PayloadTemplate(
                    module="xss",
                    title="DOM-based XSS (JavaScript sink) - Template",
                    description=(
                        "Demonstrates DOM XSS concept: untrusted data from browser sources is written to a risky sink."
                    ),
                    payload="<<XSS_TEMPLATE: DOM | CONTEXT=js | SOURCE=location | SINK=dom_write>>",
                    context="js",
                    defensive_notes=(
                        "Education-only template (non-executing).\n"
                        "- DOM XSS occurs when client-side JS writes untrusted data into dangerous sinks.\n"
                        "- Defenses: use textContent over innerHTML, sanitize with vetted libraries, CSP.\n"
                        "- Identify sources (location, storage) and sinks (DOM writes) during testing."
                    ),
                    risk_level="high",
                    tags=["dom", "context:js", "education-only", "non-executing"],
                ),
                PayloadTemplate(
                    module="xss",
                    title="Encoding Demonstration (JavaScript context) - Template",
                    description=(
                        "Non-executing marker used to demonstrate how encoding transforms representations "
                        "(URL/Base64/Hex) in a safe way."
                    ),
                    payload="<<XSS_TEMPLATE: ENCODING_DEMO | CONTEXT=js | NOTE=representation_only>>",
                    context="js",
                    defensive_notes=(
                        "Education-only template (non-executing).\n"
                        "- Encoding changes representation, not the underlying vulnerability.\n"
                        "- Correct fix is contextual output encoding + safe coding patterns.\n"
                        "- Use Proteus flags to observe how representations change safely."
                    ),
                    risk_level="low",
                    tags=["encoding", "context:js", "education-only", "non-executing"],
                ),
            ]
        )

    return items
