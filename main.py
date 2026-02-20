from __future__ import annotations

import os
import sys
from typing import Optional, Sequence

from cli import main as cli_main


# -----------------------------------------
# Runtime Configuration
# -----------------------------------------

def _configure_runtime() -> None:
    """
    Runtime ergonomics / safety (best-effort, non-fatal):

      - Prefer UTF-8 stdout/stderr where supported
      - Optional faulthandler via PROTEUS_FAULTHANDLER env var
    """

    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

    except Exception:
        # Never fail startup because of encoding adjustments
        pass

    if os.getenv("PROTEUS_FAULTHANDLER", "").strip().lower() in {"1", "true", "yes", "on"}:
        try:
            import faulthandler
            faulthandler.enable()
        except Exception:
            pass


# -----------------------------------------
# Entrypoint
# -----------------------------------------

def run(argv: Optional[Sequence[str]] = None) -> int:
    """
    Application entrypoint wrapper.

    Separates:
      - CLI layer (cli.py)
      - Runtime environment configuration
      - Future integrations (API, GUI, etc.)

    Returns proper exit codes for shell environments.
    """

    _configure_runtime()

    try:
        return cli_main(argv)

    except KeyboardInterrupt:
        print("\n[INTERRUPTED]\n", file=sys.stderr)
        return 130

    except SystemExit as e:
        code = e.code
        if isinstance(code, int):
            return code
        return 0

    except Exception as e:
        debug = os.getenv("PROTEUS_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}

        if debug:
            import traceback
            traceback.print_exc()
        else:
            print(f"\n[FATAL ERROR] {e}\n", file=sys.stderr)

        return 99


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Compatibility alias for external callers.
    """
    return run(argv)


if __name__ == "__main__":
    raise SystemExit(run())
