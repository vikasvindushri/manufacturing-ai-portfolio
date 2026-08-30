from enum import Enum
from pydantic import Field,model_validator
from .common import StrictModel,valid_id
class OutputFieldType(str,Enum):STRING="string";INTEGER="integer";NUMBER="number";BOOLEAN="boolean";DATE="date";DATETIME="datetime";ARRAY="array";OBJECT="object"
class OutputField(StrictModel):
 field_id:str;label:str=Field(min_length=1,max_length=120);field_type:OutputFieldType;required:bool=False;description:str|None=Field(None,max_length=500);enum:list[str]=Field(default_factory=list,max_length=100)
 @model_validator(mode="after")
 def valid(self):
  self.field_id=valid_id(self.field_id,"output field_id")
  if self.enum and self.field_type!=OutputFieldType.STRING:raise ValueError("enum is supported only for string output fields")
  if len(self.enum)!=len(set(self.enum)):raise ValueError("output enum values must be unique")
  return self
class OutputSchemaDefinition(StrictModel):
 schema_id:str;fields:list[OutputField]=Field(min_length=1,max_length=200)
 @model_validator(mode="after")
 def valid(self):
  self.schema_id=valid_id(self.schema_id,"schema_id");ids=[x.field_id for x in self.fields]
  if len(ids)!=len(set(ids)):raise ValueError("output field_id values must be unique")
  return self
