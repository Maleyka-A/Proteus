from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from core.models import PayloadTemplate


class TXTExportError(RuntimeError):
    """Raised when TXT export fails or validation constraints are violated."""


# -----------------------------------------
# Helpers
# -----------------------------------------

def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _atomic_write_text(path: Path, content: str) -> None:
    _ensure_parent_dir(path)

    fd: Optional[int] = None
    tmp_path: Optional[str] = None

    try:
        fd, tmp_path = tempfile.mkstemp(
            prefix=path.name + ".",
            suffix=".tmp",
            dir=str(path.parent),
        )

        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)

        fd = None
        os.replace(tmp_path, str(path))
        tmp_path = None

    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if tmp_path is not None:
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def _validate_items(items: Iterable[PayloadTemplate]) -> List[PayloadTemplate]:
    validated: List[PayloadTemplate] = []

    for i, item in enumerate(items):
        if not isinstance(item, PayloadTemplate):
            raise TXTExportError(
                f"Item at index {i} is not PayloadTemplate (got {type(item)})."
            )

        if item.disabled_by_default is not True:
            raise TXTExportError(
                f"Item at index {i} violates safety: disabled_by_default must be True."
            )

        validated.append(item)

    return validated


def _safe_str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def _get_list_field(item: PayloadTemplate, *names: str) -> List[str]:
    for n in names:
        v = getattr(item, n, None)
        if v:
            if isinstance(v, (list, tuple, set)):
                return [str(x) for x in v if str(x).strip()]
            if isinstance(v, str) and v.strip():
                return [v.strip()]
    return []


# -----------------------------------------
# Export Logic
# -----------------------------------------

def export_txt(
    items: Iterable[PayloadTemplate],
    output_path: Union[str, Path],
    *,
    include_header: bool = True,
    meta: Optional[Dict[str, Any]] = None,
    line_width: int = 72,
) -> Path:

    out = Path(output_path)

    try:
        validated = _validate_items(items)
        validated.sort(
            key=lambda x: (
                getattr(x, "module", ""),
                (_safe_str(getattr(x, "title", ""))).lower(),
            )
        )

        sep = "=" * line_width
        sub = "-" * line_width

        lines: List[str] = []

        if include_header:
            lines.append("Proteus Payload Catalog (Education-Only)")
            lines.append(f"Schema        : proteus.payloads.v1")
            lines.append(f"Exported at   : {_now_iso_utc()}")
            lines.append(f"Total entries : {len(validated)}")

            if meta:
                lines.append("Metadata:")
                for k in sorted(meta.keys(), key=lambda x: str(x)):
                    lines.append(f"  - {k}: {meta[k]}")

            lines.append(sep)
            lines.append("")

        for idx, item in enumerate(validated, start=1):
            title = _safe_str(item.title)
            module = _safe_str(item.module)
            description = _safe_str(item.description)
            payload = _safe_str(item.payload)
            risk_level = _safe_str(item.risk_level)
            disabled = "Yes" if item.disabled_by_default else "No"

            context = _safe_str(item.context)
            db_type = _safe_str(item.db_type)
            os_type = _safe_str(item.os_type)
            created_at = item.created_at

            tags = sorted(set(_get_list_field(item, "tags")))
            encodings = _get_list_field(item, "encoding_applied")
            obfuscations = _get_list_field(item, "obfuscation_applied")

            defensive_notes = _safe_str(item.defensive_notes)

            lines.append(f"[{idx}] {title}")
            lines.append(sub)

            lines.append(f"Module      : {module}")
            lines.append(f"Created at  : {created_at.isoformat()}")
            lines.append(f"Risk Level  : {risk_level}")
            lines.append(f"Disabled    : {disabled}")

            if context:
                lines.append(f"Context     : {context}")
            if db_type:
                lines.append(f"DB Type     : {db_type}")
            if os_type:
                lines.append(f"OS Type     : {os_type}")

            if tags:
                lines.append(f"Tags        : {', '.join(tags)}")
            if encodings:
                lines.append(f"Encodings   : {', '.join(encodings)}")
            if obfuscations:
                lines.append(f"Obfuscations: {', '.join(obfuscations)}")

            if description:
                lines.append("")
                lines.append("Description:")
                lines.append(description)

            lines.append("")
            lines.append("Payload Template (Non-Executing Marker):")
            lines.append(payload or "<<EMPTY_PAYLOAD_MARKER>>")

            if defensive_notes:
                lines.append("")
                lines.append("Defensive Notes:")
                lines.append(defensive_notes)

            lines.append("")
            lines.append(sep)
            lines.append("")

        content = "\n".join(lines).rstrip() + "\n"
        _atomic_write_text(out, content)

        return out

    except TXTExportError:
        raise
    except Exception as e:
        raise TXTExportError(f"TXT export failed: {e}") from e


class TXTExporter:
    def __init__(self, *, include_header: bool = True, line_width: int = 72) -> None:
        self.include_header = include_header
        self.line_width = line_width

    def export(
        self,
        items: Sequence[PayloadTemplate],
        output_path: Union[str, Path],
        *,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Path:
        return export_txt(
            items,
            output_path,
            include_header=self.include_header,
            meta=meta,
            line_width=self.line_width,
        )
