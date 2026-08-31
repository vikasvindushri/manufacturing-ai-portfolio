"""Controlled template lifecycle transitions and draft cloning."""
from __future__ import annotations
from copy import deepcopy
from phase2.models import LifecycleStatus,WorkflowDefinition
TRANSITIONS={LifecycleStatus.DRAFT:{LifecycleStatus.IN_REVIEW},LifecycleStatus.IN_REVIEW:{LifecycleStatus.DRAFT,LifecycleStatus.APPROVED},LifecycleStatus.APPROVED:{LifecycleStatus.PUBLISHED,LifecycleStatus.DRAFT},LifecycleStatus.PUBLISHED:{LifecycleStatus.ARCHIVED},LifecycleStatus.ARCHIVED:set()}
def can_transition(current:LifecycleStatus,target:LifecycleStatus)->bool:return target in TRANSITIONS[current]
def transition(workflow:WorkflowDefinition,target:LifecycleStatus)->WorkflowDefinition:
 if not can_transition(workflow.metadata.status,target):raise ValueError(f"invalid lifecycle transition: {workflow.metadata.status.value} -> {target.value}")
 updated=workflow.model_copy(deep=True);updated.metadata.status=target;return updated
def clone_as_draft(workflow:WorkflowDefinition,new_workflow_id:str,new_name:str)->WorkflowDefinition:
 payload=deepcopy(workflow.model_dump(mode="json"));payload["metadata"]["workflow_id"]=new_workflow_id;payload["metadata"]["name"]=new_name;payload["metadata"]["version"]="0.1.0";payload["metadata"]["status"]="draft"
 for prompt in payload.get("prompts",[]):prompt["status"]="draft"
 return WorkflowDefinition.model_validate(payload)
