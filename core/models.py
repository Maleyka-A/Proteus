from __future__ import annotations

from dataclasses import dataclass, field, asdict, replace
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


# ==============================
# Constants
# ==============================

VALID_MODULES = {"xss", "sqli", "cmd"}
VALID_RISK_LEVELS = {"low", "medium", "high"}

VALID_DB_TYPES = {"mysql", "postgres", "mssql"}
VALID_OS_TYPES = {"linux", "windows"}
VALID_XSS_CONTEXTS = {"html", "attr", "js"}


# ==============================
# Exceptions
# ==============================

class PayloadValidationError(Exception):
    """Raised when payload validation fails."""
    pass


# ==============================
# Payload Template Model
# ==============================

@dataclass
class PayloadTemplate:
    """
    Represents a single EDUCATIONAL payload TEMPLATE.
    """

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Core classification
    module: str = ""
    title: str = ""
    description: str = ""
    payload: str = ""

    # Context selectors
    context: Optional[str] = None
    db_type: Optional[str] = None
    os_type: Optional[str] = None

    # Transformation tracking
    encoding_applied: List[str] = field(default_factory=list)
    obfuscation_applied: List[str] = field(default_factory=list)

    # Classification tags (NEW)
    tags: List[str] = field(default_factory=list)

    # Defensive content
    defensive_notes: str = ""
    risk_level: str = "low"

    # Safety flag
    disabled_by_default: bool = True

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ======================================
    # Post Initialization Validation
    # ======================================

    def __post_init__(self) -> None:
        self._validate()

    # ======================================
    # Validation Logic
    # ======================================

    def _validate(self) -> None:

        if self.module not in VALID_MODULES:
            raise PayloadValidationError(
                f"Invalid module '{self.module}'. Must be one of {sorted(VALID_MODULES)}"
            )

        if not isinstance(self.title, str) or not self.title.strip():
            raise PayloadValidationError("title cannot be empty.")

        if not isinstance(self.payload, str) or not self.payload.strip():
            raise PayloadValidationError("payload cannot be empty.")

        if self.risk_level not in VALID_RISK_LEVELS:
            raise PayloadValidationError(
                f"Invalid risk_level '{self.risk_level}'. Must be one of {sorted(VALID_RISK_LEVELS)}"
            )

        if self.disabled_by_default is not True:
            raise PayloadValidationError("disabled_by_default must remain True for safety.")

        # Validate tags
        if not isinstance(self.tags, list):
            raise PayloadValidationError("tags must be a list of strings.")
        for tag in self.tags:
            if not isinstance(tag, str):
                raise PayloadValidationError("each tag must be a string.")

        # Module-specific rules
        if self.module == "xss":
            if self.context not in VALID_XSS_CONTEXTS:
                raise PayloadValidationError(
                    f"For module 'xss', context must be one of {sorted(VALID_XSS_CONTEXTS)}"
                )
            if self.db_type is not None:
                raise PayloadValidationError("db_type must be None for module 'xss'.")
            if self.os_type is not None:
                raise PayloadValidationError("os_type must be None for module 'xss'.")

        elif self.module == "sqli":
            if not self.db_type:
                raise PayloadValidationError("db_type is required for module 'sqli'.")
            if self.db_type not in VALID_DB_TYPES:
                raise PayloadValidationError(
                    f"Invalid db_type '{self.db_type}'. Must be one of {sorted(VALID_DB_TYPES)}"
                )
            if self.context is not None:
                raise PayloadValidationError("context must be None for module 'sqli'.")
            if self.os_type is not None:
                raise PayloadValidationError("os_type must be None for module 'sqli'.")

        elif self.module == "cmd":
            if not self.os_type:
                raise PayloadValidationError("os_type is required for module 'cmd'.")
            if self.os_type not in VALID_OS_TYPES:
                raise PayloadValidationError(
                    f"Invalid os_type '{self.os_type}'. Must be one of {sorted(VALID_OS_TYPES)}"
                )
            if self.context is not None:
                raise PayloadValidationError("context must be None for module 'cmd'.")
            if self.db_type is not None:
                raise PayloadValidationError("db_type must be None for module 'cmd'.")

        if self.created_at.tzinfo is None:
            raise PayloadValidationError("created_at must be timezone-aware (UTC).")

    # ======================================
    # Transformation Tracking
    # ======================================

    def add_encoding(self, encoding_name: str) -> None:
        self.encoding_applied.append(encoding_name)

    def add_obfuscation(self, technique_name: str) -> None:
        self.obfuscation_applied.append(technique_name)

    # ======================================
    # Immutable Clone
    # ======================================

    def clone_with_updates(self, **kwargs) -> "PayloadTemplate":
        return replace(self, **kwargs)

    # ======================================
    # Export Helpers
    # ======================================

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data

    def to_json_safe(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "module": self.module,
            "title": self.title,
            "description": self.description,
            "payload": self.payload,
            "context": self.context,
            "db_type": self.db_type,
            "os_type": self.os_type,
            "encoding_applied": list(self.encoding_applied),
            "obfuscation_applied": list(self.obfuscation_applied),
            "tags": list(self.tags),
            "defensive_notes": self.defensive_notes,
            "risk_level": self.risk_level,
            "disabled_by_default": self.disabled_by_default,
            "created_at": self.created_at.isoformat(),
        }

    # ======================================
    # Representation
    # ======================================

    def __repr__(self) -> str:
        return (
            f"<PayloadTemplate "
            f"id={self.id[:8]} "
            f"module={self.module} "
            f"title='{self.title}' "
            f"risk={self.risk_level} "
            f"disabled={self.disabled_by_default}>"
        )
