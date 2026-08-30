from pydantic import Field,model_validator
from .approval import ApprovalPolicy
from .common import StrictModel,LifecycleStatus,SEMVER_PATTERN,find_secret_paths,valid_id
from .field import FieldDefinition
from .output import OutputSchemaDefinition
from .policy import AIPolicy,DataClassification
from .prompt import PromptTemplate
from .routing import RoutingAction
from .rule import RuleDefinition
from .test_case import SyntheticTestCase
class WorkflowMetadata(StrictModel):
 workflow_id:str;name:str=Field(min_length=3,max_length=120);description:str=Field(min_length=10,max_length=1000);version:str=Field(pattern=SEMVER_PATTERN);owner:str=Field(min_length=2,max_length=120);status:LifecycleStatus=LifecycleStatus.DRAFT;definition_version:str="1.1";tags:list[str]=Field(default_factory=list,max_length=20)
 @model_validator(mode="after")
 def valid(self):self.workflow_id=valid_id(self.workflow_id,"workflow_id");return self
class WorkflowDefinition(StrictModel):
 metadata:WorkflowMetadata;fields:list[FieldDefinition]=Field(min_length=1,max_length=100);rules:list[RuleDefinition]=Field(default_factory=list,max_length=200);routing_actions:list[RoutingAction]=Field(default_factory=list,max_length=200);prompts:list[PromptTemplate]=Field(default_factory=list,max_length=50);output_schemas:list[OutputSchemaDefinition]=Field(default_factory=list,max_length=20);ai_policy:AIPolicy=Field(default_factory=AIPolicy);allowed_input_classifications:list[DataClassification]=Field(default_factory=lambda:list(DataClassification));approval:ApprovalPolicy=Field(default_factory=ApprovalPolicy);test_cases:list[SyntheticTestCase]=Field(default_factory=list,max_length=50);extensions:dict=Field(default_factory=dict)
 @model_validator(mode="after")
 def refs(self):
  groups=[([x.field_id for x in self.fields],"field_id"),([x.rule_id for x in self.rules],"rule_id"),([x.action_id for x in self.routing_actions],"action_id"),([x.prompt_id for x in self.prompts],"prompt_id"),([x.schema_id for x in self.output_schemas],"schema_id"),([x.test_case_id for x in self.test_cases],"test_case_id")]
  for vals,label in groups:
   if len(vals)!=len(set(vals)):raise ValueError(f"{label} values must be unique")
  fields,rules,actions,prompts,schemas=[set(x[0]) for x in groups[:5]]
  unknown=sorted({x.field_id for x in self.rules}-fields)
  if unknown:raise ValueError(f"rules reference unknown fields: {unknown}")
  unknown=sorted({x.when_rule_id for x in self.routing_actions}-rules)
  if unknown:raise ValueError(f"routing actions reference unknown rules: {unknown}")
  unknown=sorted({x.response_schema_id for x in self.prompts if x.response_schema_id}-schemas)
  if unknown:raise ValueError(f"prompts reference unknown output schemas: {unknown}")
  if self.ai_policy.prompt_template_id and self.ai_policy.prompt_template_id not in prompts:raise ValueError("AI policy references unknown prompt template")
  for c in self.test_cases:
   if set(c.input)-fields:raise ValueError(f"test case {c.test_case_id} uses unknown inputs")
   if not set(c.expected_rule_ids)<=rules:raise ValueError(f"test case {c.test_case_id} references unknown rules")
   if not set(c.expected_routing_action_ids)<=actions:raise ValueError(f"test case {c.test_case_id} references unknown routing actions")
  paths=find_secret_paths(self.model_dump(mode="json"))
  if paths:raise ValueError(f"workflow definitions cannot contain secrets: {paths}")
  return self
