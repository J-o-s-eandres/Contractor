import json
import os
import shutil
import subprocess
import sys

from contractor.models import BreakingChange
from contractor.oasdiff_adapter import adapt_changes

OASDIFF_NOT_FOUND_MSG = (
    "oasdiff not found. Install it with:\n"
    "  brew install oasdiff\n"
    "  go install github.com/oasdiff/oasdiff@latest\n"
    "  docker run --rm -v $PWD:/specs oasdiff/oasdiff breaking ...\n"
    "Or use --engine legacy to fall back to the built-in basic detection.\n"
    "See: https://github.com/oasdiff/oasdiff#installation"
)


def run_oasdiff(
    base: str,
    candidate: str,
    fail_on: str = "ERR",
    **kwargs,
) -> tuple[list[BreakingChange], int]:
    binary = _find_binary()

    cmd = [
        binary,
        "breaking",
        "--format",
        "json",
        "--fail-on",
        fail_on,
        "--include-path-params",
        base,
        candidate,
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode >= 2:
        msg = proc.stderr.strip() or proc.stdout.strip() or "unknown error"
        print(f"oasdiff error (exit {proc.returncode}): {msg}", file=sys.stderr)
        sys.exit(proc.returncode == 2)

    raw = json.loads(proc.stdout) if proc.stdout.strip() else []
    changes = adapt_changes(raw)

    return changes, proc.returncode


def _find_binary() -> str:
    path = shutil.which("oasdiff")
    if path:
        return path
    bundled = os.path.join(os.path.dirname(sys.argv[0]), "oasdiff")
    if os.path.exists(bundled):
        return bundled
    bundled_exe = bundled + ".exe"
    if os.path.exists(bundled_exe):
        return bundled_exe
    raise FileNotFoundError(OASDIFF_NOT_FOUND_MSG)
