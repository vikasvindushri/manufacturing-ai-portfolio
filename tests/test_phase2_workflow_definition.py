import json
from pathlib import Path

import pytest

from phase2.models import WorkflowDefinition
from phase2.registry.loader import WorkflowLoadError, load_workflow, load_workflow_text

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "phase2" / "templates" / "quality_8d.json"


def test_starter_template_validates():
    workflow = load_workflow(TEMPLATE)
    assert workflow.metadata.workflow_id == "quality_8d_v1"
    assert workflow.approval.required is True


def test_generated_json_schema_is_strict():
    schema = WorkflowDefinition.model_json_schema()
    assert schema["additionalProperties"] is False
    assert "metadata" in schema["required"]


def test_unknown_rule_field_is_rejected():
    payload = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    payload["rules"][0]["field_id"] = "missing_field"
    with pytest.raises(WorkflowLoadError, match="unknown fields"):
        load_workflow_text(json.dumps(payload))


def test_approval_cannot_be_disabled():
    payload = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    payload["approval"]["required"] = False
    with pytest.raises(WorkflowLoadError, match="human approval is mandatory"):
        load_workflow_text(json.dumps(payload))


def test_secret_fields_are_rejected():
    payload = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    payload["extensions"] = {"api_key": "must-not-be-here"}
    with pytest.raises(WorkflowLoadError, match="cannot contain secrets"):
        load_workflow_text(json.dumps(payload))


def test_extra_properties_are_rejected():
    payload = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    payload["unexpected"] = True
    with pytest.raises(WorkflowLoadError):
        load_workflow_text(json.dumps(payload))
