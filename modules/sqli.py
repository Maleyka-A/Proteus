from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Sequence

from core.models import PayloadTemplate
from core.registry import registry

DBType = Literal["mysql", "postgres", "mssql"]

# -----------------------------------------
# DB Normalization (with aliases)
# -----------------------------------------

_VALID_DB_TYPES: Dict[str, DBType] = {
    "mysql": "mysql",
    "mariadb": "mysql",
    "postgres": "postgres",
    "postgresql": "postgres",
    "mssql": "mssql",
    "sqlserver": "mssql",
    "sql server": "mssql",
}


def _normalize_db(db_type: str) -> DBType:
    raw = (db_type or "").strip().lower()
    db = _VALID_DB_TYPES.get(raw)
    if not db:
        supported = sorted({v for v in _VALID_DB_TYPES.values()})
        raise ValueError(
            f"Invalid db_type '{db_type}'. Supported: {supported}"
        )
    return db


# -----------------------------------------
# DB-Specific Defensive Notes
# -----------------------------------------

def _db_defense_highlights(db: DBType) -> str:
    if db == "mysql":
        return (
            "- MySQL/MariaDB: disable verbose errors in production.\n"
            "- Monitor slow query log and restrict SUPER/FILE privileges.\n"
        )

    if db == "postgres":
        return (
            "- PostgreSQL: enforce least-privilege roles.\n"
            "- Avoid dynamic SQL inside functions.\n"
        )

    return (
        "- SQL Server: avoid string concatenation with EXEC().\n"
        "- Review stored procedures for dynamic SQL usage.\n"
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
        key="ERROR_BASED",
        title="Error-Based SQLi",
        risk="high",
        tags=("error-based", "education-only", "non-executing"),
        description=(
            "Concept: database error messages may leak query structure "
            "when input is concatenated into SQL statements."
        ),
        defensive_notes=(
            "- Root cause: dynamic SQL string construction.\n"
            "- Use parameterized queries / prepared statements.\n"
            "- Suppress detailed DB errors in production.\n"
        ),
    ),
    _TemplateSpec(
        key="UNION_BASED",
        title="Union-Based SQLi",
        risk="high",
        tags=("union-based", "education-only", "non-executing"),
        description=(
            "Concept: attacker-controlled input may alter SELECT queries "
            "to combine additional result sets."
        ),
        defensive_notes=(
            "- Use parameterized queries.\n"
            "- Apply least-privilege DB roles.\n"
            "- Avoid direct string interpolation in SQL.\n"
        ),
    ),
    _TemplateSpec(
        key="BLIND_BOOLEAN",
        title="Blind SQLi (Boolean-Based)",
        risk="medium",
        tags=("blind", "boolean-based", "education-only", "non-executing"),
        description=(
            "Concept: response differences reveal true/false evaluation "
            "even without visible errors."
        ),
        defensive_notes=(
            "- Enforce consistent responses.\n"
            "- Use parameterized queries.\n"
            "- Avoid logic branching on raw user input.\n"
        ),
    ),
    _TemplateSpec(
        key="BLIND_TIME",
        title="Blind SQLi (Time-Based)",
        risk="medium",
        tags=("blind", "time-based", "education-only", "non-executing"),
        description=(
            "Concept: response latency may indicate conditional execution."
        ),
        defensive_notes=(
            "- Set DB query time limits.\n"
            "- Monitor abnormal latency patterns.\n"
            "- Use parameterization everywhere.\n"
        ),
    ),
    _TemplateSpec(
        key="BYPASS_CONCEPTS",
        title="Filter Evasion Concepts (Comments / Case)",
        risk="low",
        tags=("bypass-concepts", "education-only", "non-executing"),
        description=(
            "Concept: naive keyword filters fail against case changes "
            "or token splitting."
        ),
        defensive_notes=(
            "- Do not rely on regex keyword filtering.\n"
            "- Use parameterized queries as primary defense.\n"
        ),
    ),
)


# -----------------------------------------
# Generator
# -----------------------------------------

@registry.register_module("sqli", requires_db=True)
def generate_payloads(*, db_type: str) -> List[PayloadTemplate]:
    """
    Educational SQL Injection template generator (NON-EXECUTING).
    """

    db = _normalize_db(db_type)

    db_tag = f"db:{db}"
    db_specific_notes = _db_defense_highlights(db)

    items: List[PayloadTemplate] = []

    for spec in _TEMPLATES:

        marker = (
            f"<<SQLI_TEMPLATE: {spec.key} | "
            f"DB={db} | NON_EXECUTING>>"
        )

        combined_notes = (
            "Education-only (non-executing).\n"
            f"{spec.defensive_notes}"
            f"{db_specific_notes}"
            "- Integrate SAST/DAST and code review for query construction.\n"
        )

        items.append(
            PayloadTemplate(
                module="sqli",
                title=f"{spec.title} ({db}) - Template",
                description=spec.description,
                payload=marker,
                db_type=db,
                defensive_notes=combined_notes,
                risk_level=spec.risk,
                tags=[*spec.tags, db_tag],
            )
        )

    return items
