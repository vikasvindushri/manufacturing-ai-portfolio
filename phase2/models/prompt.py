from pydantic import Field,model_validator
from .common import StrictModel,LifecycleStatus,SEMVER_PATTERN,find_secret_paths,valid_id
class PromptTemplate(StrictModel):
 prompt_id:str;version:str=Field(pattern=SEMVER_PATTERN);status:LifecycleStatus=LifecycleStatus.DRAFT;system_instruction:str=Field(min_length=10,max_length=8000);task_template:str=Field(min_length=10,max_length=16000);variables:list[str]=Field(default_factory=list,max_length=50);response_schema_id:str|None=None
 @model_validator(mode="after")
 def valid(self):
  self.prompt_id=valid_id(self.prompt_id,"prompt_id")
  if self.response_schema_id:self.response_schema_id=valid_id(self.response_schema_id,"response_schema_id")
  if len(self.variables)!=len(set(self.variables)):raise ValueError("prompt variables must be unique")
  if find_secret_paths(self.model_dump(mode="json")):raise ValueError("prompt templates cannot contain secret properties")
  return self
