from pydantic import Field,model_validator
from .common import StrictModel
class ApprovalPolicy(StrictModel):
 required:bool=True;minimum_approvals:int=Field(1,ge=1,le=10);allowed_roles:list[str]=Field(default_factory=lambda:["workflow_reviewer"],min_length=1,max_length=20);rationale_required:bool=True;creator_may_approve:bool=False
 @model_validator(mode="after")
 def valid(self):
  if not self.required:raise ValueError("human approval is mandatory for governed workflows")
  if len(self.allowed_roles)!=len(set(self.allowed_roles)):raise ValueError("approval roles must be unique")
  return self
