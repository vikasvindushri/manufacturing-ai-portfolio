from enum import Enum
from pydantic import Field,model_validator
from .common import StrictModel,valid_id
class DataClassification(str,Enum):SYNTHETIC="synthetic";PUBLIC="public";INTERNAL_NON_SENSITIVE="internal_non_sensitive";CONFIDENTIAL_RESTRICTED="confidential_restricted"
class AICapability(str,Enum):STRUCTURED_REVIEW="structured_review";GROUNDED_SYNTHESIS="grounded_synthesis";SEMANTIC_SEARCH="semantic_search"
class AIPolicy(StrictModel):
 enabled:bool=False;capability:AICapability|None=None;prompt_template_id:str|None=None;allowed_classifications:list[DataClassification]=Field(default_factory=lambda:[DataClassification.SYNTHETIC,DataClassification.PUBLIC,DataClassification.INTERNAL_NON_SENSITIVE]);fallback:str="local_result";human_approval_required:bool=True
 @model_validator(mode="after")
 def valid(self):
  if self.enabled and (not self.capability or not self.prompt_template_id):raise ValueError("enabled AI policy requires capability and prompt_template_id")
  if self.prompt_template_id:self.prompt_template_id=valid_id(self.prompt_template_id,"prompt_template_id")
  if DataClassification.CONFIDENTIAL_RESTRICTED in self.allowed_classifications:raise ValueError("confidential_restricted cannot use external AI")
  if self.fallback!="local_result":raise ValueError("Phase 2 requires local_result fallback")
  if not self.human_approval_required:raise ValueError("AI-assisted workflows require human approval")
  return self
