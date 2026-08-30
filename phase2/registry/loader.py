"""Safe loading for versioned workflow definitions."""
from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from phase2.models import WorkflowDefinition

MAX_DEFINITION_BYTES = 1_000_000


class WorkflowLoadError(ValueError):
    pass


def load_workflow_text(text: str) -> WorkflowDefinition:
    if len(text.encode("utf-8")) > MAX_DEFINITION_BYTES:
        raise WorkflowLoadError("workflow definition exceeds the 1 MB limit")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise WorkflowLoadError(f"invalid JSON at line {exc.lineno}, column {exc.colno}") from exc
    if not isinstance(payload, dict):
        raise WorkflowLoadError("workflow definition must be a JSON object")
    try:
        return WorkflowDefinition.model_validate(payload)
    except ValidationError as exc:
        raise WorkflowLoadError(str(exc)) from exc


def load_workflow(path: str | Path) -> WorkflowDefinition:
    source = Path(path)
    if source.suffix.lower() != ".json":
        raise WorkflowLoadError("workflow definitions must use the .json extension")
    if not source.is_file():
        raise WorkflowLoadError(f"workflow definition not found: {source}")
    if source.stat().st_size > MAX_DEFINITION_BYTES:
        raise WorkflowLoadError("workflow definition exceeds the 1 MB limit")
    return load_workflow_text(source.read_text(encoding="utf-8"))
