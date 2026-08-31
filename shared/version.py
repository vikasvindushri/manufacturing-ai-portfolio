"""Single source of truth for the application development version."""
from pathlib import Path

_VERSION_FILE = Path(__file__).resolve().parents[1] / "VERSION"
__version__ = _VERSION_FILE.read_text(encoding="utf-8").strip()
STABLE_RELEASE = "0.6"
PHASE_STATUS = "Phase 2 in development - Increment 2.1 complete"
WORKFLOW_DEFINITION_VERSION = "1.1"
