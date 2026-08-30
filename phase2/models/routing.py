from enum import Enum
from pydantic import Field,model_validator
from .common import StrictModel,valid_id
class RoutingActionType(str,Enum):
 ASSIGN_ROLE="assign_role";SET_SEVERITY="set_severity";SET_CATEGORY="set_category";REQUIRE_APPROVAL="require_approval";ESCALATE="escalate";REQUIRE_FOLLOW_UP="require_follow_up"
class RoutingAction(StrictModel):
 action_id:str;when_rule_id:str;action_type:RoutingActionType;value:str=Field(min_length=1,max_length=200)
 @model_validator(mode="after")
 def ids(self):self.action_id=valid_id(self.action_id,"action_id");self.when_rule_id=valid_id(self.when_rule_id,"when_rule_id");return self
