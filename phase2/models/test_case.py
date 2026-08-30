from typing import Any
from pydantic import Field,model_validator
from .common import StrictModel,find_secret_paths,valid_id
from .policy import DataClassification
class SyntheticTestCase(StrictModel):
 test_case_id:str;name:str=Field(min_length=3,max_length=120);classification:DataClassification=DataClassification.SYNTHETIC;input:dict[str,Any];expected_rule_ids:list[str]=Field(default_factory=list);expected_routing_action_ids:list[str]=Field(default_factory=list)
 @model_validator(mode="after")
 def valid(self):
  self.test_case_id=valid_id(self.test_case_id,"test_case_id")
  if self.classification!=DataClassification.SYNTHETIC:raise ValueError("committed preview test cases must be synthetic")
  if find_secret_paths(self.input):raise ValueError("test cases cannot contain secrets")
  return self
