from enum import Enum
from typing import Any
from pydantic import Field,model_validator
from .common import StrictModel,valid_id
class FieldType(str,Enum):
 TEXT="text";TEXTAREA="textarea";INTEGER="integer";NUMBER="number";BOOLEAN="boolean";DATE="date";DATETIME="datetime";SELECT="select";MULTISELECT="multiselect"
class ValidationConstraint(StrictModel):
 minimum:float|None=None;maximum:float|None=None;min_length:int|None=Field(None,ge=0);max_length:int|None=Field(None,ge=1);pattern:str|None=None
 @model_validator(mode="after")
 def valid_ranges(self):
  if self.minimum is not None and self.maximum is not None and self.minimum>self.maximum:raise ValueError("minimum cannot exceed maximum")
  if self.min_length is not None and self.max_length is not None and self.min_length>self.max_length:raise ValueError("min_length cannot exceed max_length")
  return self
class FieldDefinition(StrictModel):
 field_id:str;label:str=Field(min_length=1,max_length=120);field_type:FieldType;required:bool=False;help_text:str|None=Field(None,max_length=500);default:Any=None;options:list[str]=Field(default_factory=list,max_length=100);sensitive:bool=False;validation:ValidationConstraint|None=None
 @model_validator(mode="after")
 def valid(self):
  self.field_id=valid_id(self.field_id,"field_id");sel=self.field_type in {FieldType.SELECT,FieldType.MULTISELECT}
  if sel and not self.options:raise ValueError("select and multiselect fields require options")
  if not sel and self.options:raise ValueError("options are only valid for select and multiselect fields")
  if len(self.options)!=len(set(self.options)):raise ValueError("field options must be unique")
  return self
