from enum import Enum
from typing import Any
from pydantic import Field,model_validator
from .common import StrictModel,valid_id
class RuleOperator(str,Enum):
 EQUALS="equals";NOT_EQUALS="not_equals";CONTAINS="contains";GREATER_THAN="greater_than";LESS_THAN="less_than";IN="in"
class RuleDefinition(StrictModel):
 rule_id:str;field_id:str;operator:RuleOperator;value:Any;message:str=Field(min_length=3,max_length=300);enabled:bool=True;priority:int=Field(100,ge=0,le=10000)
 @model_validator(mode="after")
 def ids(self):self.rule_id=valid_id(self.rule_id,"rule_id");self.field_id=valid_id(self.field_id,"field_id");return self
