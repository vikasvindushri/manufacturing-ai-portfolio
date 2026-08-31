from pathlib import Path
import pytest
from phase2.models import DataClassification,LifecycleStatus
from phase2.registry import available_tags,can_transition,clone_as_draft,get_template,list_templates,search_templates,transition

def test_catalog_has_five_unique_templates():
 items=list_templates();assert len(items)==5;assert len({x.workflow_id for x in items})==5
@pytest.mark.parametrize("workflow_id",["quality_8d_v1","nonconformance_v1","fault_triage_v1","layered_process_audit_v1","knowledge_search_v1"])
def test_template_validates(workflow_id):
 w=get_template(workflow_id);assert w.metadata.definition_version=="1.1";assert w.approval.required;assert w.test_cases;assert all(x.classification==DataClassification.SYNTHETIC for x in w.test_cases);assert w.ai_policy.fallback=="local_result";assert DataClassification.CONFIDENTIAL_RESTRICTED not in w.ai_policy.allowed_classifications
def test_search_and_filter():
 assert {x.workflow_id for x in search_templates("fault")}=={"fault_triage_v1"};assert search_templates(tag="quality");assert "knowledge" in available_tags()
def test_clone_is_draft_and_does_not_mutate_source():
 source=get_template("quality_8d_v1");draft=clone_as_draft(source,"quality_8d_custom","Custom Quality 8D");assert draft.metadata.status==LifecycleStatus.DRAFT;assert draft.metadata.version=="0.1.0";assert source.metadata.workflow_id=="quality_8d_v1"
def test_lifecycle_controls():
 workflow=get_template("nonconformance_v1");review=transition(workflow,LifecycleStatus.IN_REVIEW);approved=transition(review,LifecycleStatus.APPROVED);assert approved.metadata.status==LifecycleStatus.APPROVED;assert not can_transition(LifecycleStatus.DRAFT,LifecycleStatus.PUBLISHED)
def test_invalid_transition_rejected():
 with pytest.raises(ValueError):transition(get_template("fault_triage_v1"),LifecycleStatus.PUBLISHED)
