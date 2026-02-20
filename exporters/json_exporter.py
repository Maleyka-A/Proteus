from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from core.models import PayloadTemplate


class JSONExportError(RuntimeError):
    """Raised when JSON export fails or the input violates export constraints."""


def _now_iso() -> str:
    """Return UTC ISO timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _validate_items(items: Iterable[PayloadTemplate]) -> List[PayloadTemplate]:
    """
    Validate and materialize iterable into a list.
    Enforces project safety: disabled_by_default must remain True.
    """
    validated: List[PayloadTemplate] = []

    for i, item in enumerate(items):
        if not isinstance(item, PayloadTemplate):
            raise JSONExportError(
                f"Item at index {i} is not PayloadTemplate (got {type(item)})."
            )

        if item.disabled_by_default is not True:
            raise JSONExportError(
                f"Item at index {i} violates safety: disabled_by_default must be True."
            )

        if not callable(getattr(item, "to_json_safe", None)):
            raise JSONExportError(
                f"Item at index {i} does not implement to_json_safe()."
            )

        validated.append(item)

    return validated


def _atomic_write_text(path: Path, content: str) -> None:
    """
    Atomic write to prevent partial/corrupt files.
    """
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


def export_json(
    items: Iterable[PayloadTemplate],
    output_path: Union[str, Path],
    *,
    pretty: bool = True,
    include_wrapper: bool = True,
    meta: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Export payload templates to structured JSON catalog.

    Features:
    - strict validation
    - deterministic ordering
    - optional wrapper schema
    - atomic write
    - UTF-8 output
    """

    out = Path(output_path)

    try:
        validated = _validate_items(items)

        # Deterministic ordering (helps diff/CI)
        validated.sort(key=lambda x: (x.module, (x.title or "").lower()))

        payloads = [t.to_json_safe() for t in validated]

        if include_wrapper:
            doc: Dict[str, Any] = {
                "schema": "proteus.payloads.v1",
                "exported_at": _now_iso(),
                "count": len(payloads),
                "payloads": payloads,
            }

            if meta:
                reserved = {"schema", "exported_at", "count", "payloads"}
                collisions = reserved.intersection(meta.keys())
                if collisions:
                    raise JSONExportError(
                        f"meta contains reserved keys: {sorted(collisions)}"
                    )
                doc["meta"] = dict(meta)

        else:
            doc = payloads

        json_text = json.dumps(
            doc,
            indent=2 if pretty else None,
            ensure_ascii=False,
            sort_keys=pretty,
        ) + "\n"

        _atomic_write_text(out, json_text)
        return out

    except JSONExportError:
        raise
    except Exception as e:
        raise JSONExportError(f"JSON export failed: {e}") from e


class JSONExporter:
    """
    OOP wrapper for pipeline.export() usage.
    """

    def __init__(self, *, pretty: bool = True, include_wrapper: bool = True) -> None:
        self.pretty = pretty
        self.include_wrapper = include_wrapper

    def export(
        self,
        items: Sequence[PayloadTemplate],
        output_path: Union[str, Path],
        *,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Path:
        return export_json(
            items,
            output_path,
            pretty=self.pretty,
            include_wrapper=self.include_wrapper,
            meta=meta,
        )
