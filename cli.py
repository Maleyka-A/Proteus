from __future__ import annotations
from version import __version__
import argparse
import sys
from pathlib import Path
from typing import Dict, Optional, Sequence

from core.pipeline import PipelineError, run_pipeline
from transforms.encoder import list_supported_encodings
from transforms.obfuscator import list_supported_obfuscations


class CLIError(RuntimeError):
    """Raised for CLI validation / usage errors."""


# -----------------------------------------
# Helpers
# -----------------------------------------

def _default_output_path(export_format: str) -> str:
    ext = export_format.lower()
    return str(Path("samples") / f"sample_payloads.{ext}")


def _parse_meta(meta_args: Optional[Sequence[str]]) -> Optional[Dict[str, str]]:
    if not meta_args:
        return None

    meta: Dict[str, str] = {}

    for pair in meta_args:
        if "=" not in pair:
            raise CLIError(f"Invalid meta '{pair}'. Expected key=value.")

        key, value = pair.split("=", 1)
        key = key.strip()

        if not key:
            raise CLIError(f"Invalid meta '{pair}'. Key must be non-empty.")

        meta[key] = value.strip()

    return meta


def _enforce_selectors(
    module: str,
    *,
    context: Optional[str],
    db: Optional[str],
    os_type: Optional[str],
) -> None:
    """
    CLI-level guardrails (registry/models also enforce).
    """
    if module == "xss" and not context:
        raise CLIError("Module 'xss' requires --context {html,attr,js}.")

    if module == "sqli" and not db:
        raise CLIError("Module 'sqli' requires --db {mysql,postgres,mssql}.")

    if module == "cmd" and not os_type:
        raise CLIError("Module 'cmd' requires --os {linux,windows}.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="proteus",
        description=(
            "Proteus — Educational Offensive Payload Framework (NON-EXECUTING)\n"
            "Generates inert marker templates only.\n"
            "No network, no DB, no command execution."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # Global version flag
    from config import __version__

    parser.add_argument(
        "--version",
        action="version",
        version=f"Proteus {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate payload templates (optionally transform and export)",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    generate_parser.add_argument(
        "--module",
        required=True,
        choices=["xss", "sqli", "cmd"],
        help="Module to use (xss | sqli | cmd)",
    )

    # Selectors
    generate_parser.add_argument(
        "--context",
        choices=["html", "attr", "js"],
        help="XSS context selector",
    )

    generate_parser.add_argument(
        "--db",
        choices=["mysql", "postgres", "mssql"],
        help="SQLi DB selector",
    )

    generate_parser.add_argument(
        "--os",
        choices=["linux", "windows"],
        help="CMD OS selector",
    )

    # Transforms
    generate_parser.add_argument(
        "--encode",
        choices=list_supported_encodings(),
        help="Apply encoding transformation",
    )

    generate_parser.add_argument(
        "--obfuscate",
        choices=list_supported_obfuscations(),
        help="Apply obfuscation transformation",
    )

    # Export
    generate_parser.add_argument(
        "--export",
        choices=["json", "txt"],
        help="Export format. If omitted, prints preview only.",
    )

    generate_parser.add_argument(
        "--output",
        help="Output file path (default: samples/sample_payloads.<ext>)",
    )

    # Metadata
    generate_parser.add_argument(
        "--meta",
        nargs="*",
        help="Optional metadata key=value pairs (used by exporters)",
    )

    return parser


# -----------------------------------------
# Main
# -----------------------------------------

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        if args.command != "generate":
            raise CLIError("Unknown command.")

        module = args.module
        context = args.context
        db = args.db
        os_type = args.os

        _enforce_selectors(module, context=context, db=db, os_type=os_type)

        meta_dict = _parse_meta(args.meta)

        export_format = args.export
        output_path = args.output

        if export_format and not output_path:
            output_path = _default_output_path(export_format)

        items = run_pipeline(
            module=module,
            db_type=db,
            os_type=os_type,
            context=context,
            encoding=args.encode,
            obfuscation=args.obfuscate,
            export_format=export_format,
            output_path=output_path,
            meta=meta_dict,
        )

        print(f"\n✔ Generated {len(items)} template(s).\n")

        if not export_format:
            for i, item in enumerate(items, start=1):
                print(f"[{i}] {item.title}")
            print()
        else:
            print(f"✔ Export completed ({export_format.upper()})")
            print(f"Output: {output_path}\n")

        return 0

    except (CLIError, PipelineError) as e:
        print(f"\n[ERROR] {e}\n", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\n[INTERRUPTED]\n", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] {e}\n", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
