import json
from pathlib import Path
import pytest
from phase2.models import WorkflowDefinition
from phase2.registry import check_definition_version,load_workflow,validate_payload
P=Path(__file__).resolve().parents[1]/"phase2/templates/quality_8d.json"
def data():return json.loads(P.read_text())
def test_template():assert load_workflow(P).metadata.definition_version=="1.1"
def test_schema_strict():assert WorkflowDefinition.model_json_schema()["additionalProperties"] is False
def test_confidential_ai_rejected():
 x=data();x["ai_policy"]["allowed_classifications"].append("confidential_restricted");assert not validate_payload(x)["valid"]
def test_unknown_prompt():x=data();x["ai_policy"]["prompt_template_id"]="missing_prompt";assert not validate_payload(x)["valid"]
def test_unknown_schema():x=data();x["prompts"][0]["response_schema_id"]="missing_schema";assert not validate_payload(x)["valid"]
def test_unknown_route_rule():x=data();x["routing_actions"][0]["when_rule_id"]="missing_rule";assert not validate_payload(x)["valid"]
def test_non_synthetic_case():x=data();x["test_cases"][0]["classification"]="public";assert not validate_payload(x)["valid"]
def test_nested_secret():x=data();x["extensions"]={"provider":{"client_secret":"nope"}};assert not validate_payload(x)["valid"]
@pytest.mark.parametrize("v,ok",[("1.0",True),("1.1",True),("1.2",False),("2.0",False),(None,False),("bad",False)])
def test_compatibility(v,ok):assert check_definition_version(v).compatible is ok
def test_structured_errors():x=data();x["rules"][0]["field_id"]="missing";assert validate_payload(x)["errors"]
