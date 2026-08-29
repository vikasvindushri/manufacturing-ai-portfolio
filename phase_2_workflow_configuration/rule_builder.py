"""Phase 2 Rule Builder - Create routing, approval, and categorization rules"""
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field
from datetime import datetime
from phase_2_workflow_configuration.schemas import (
    WorkflowRule,
    Condition,
    RuleAction,
    Operator,
    LogicOperator,
)

class RuleBuilderError(Exception):
    """Rule builder operation error"""
    pass

class RuleDraft(BaseModel):
    """Rule under construction"""
    id: str
    workflow_id: str
    name: str
    description: Optional[str] = None
    enabled: bool = True
    conditions: List[Condition] = Field(default_factory=list)
    logic: LogicOperator = LogicOperator.AND
    actions: List[RuleAction] = Field(default_factory=list)
    priority: int = 0
    test_data: Optional[Dict[str, Any]] = None  # for testing
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RuleBuilder:
    """Builder for creating and managing workflow rules"""
    
    def __init__(self):
        self.current_rule: Optional[RuleDraft] = None
    
    # ========================================================================
    # RULE LIFECYCLE
    # ========================================================================
    
    def create_rule(
        self,
        workflow_id: str,
        rule_id: str,
        name: str,
        created_by: str,
    ) -> RuleDraft:
        """Create a new rule draft"""
        self.current_rule = RuleDraft(
            id=rule_id,
            workflow_id=workflow_id,
            name=name,
            created_by=created_by,
        )
        return self.current_rule
    
    def load_rule(self, rule_draft: RuleDraft) -> RuleDraft:
        """Load an existing rule draft for editing"""
        self.current_rule = rule_draft
        return self.current_rule
    
    def get_rule(self) -> Optional[RuleDraft]:
        """Get the current rule being edited"""
        return self.current_rule
    
    # ========================================================================
    # CONDITION MANAGEMENT
    # ========================================================================
    
    def add_condition(
        self,
        field_id: str,
        operator: Operator,
        value: Any,
    ) -> Condition:
        """Add a condition to the rule"""
        if not self.current_rule:
            raise RuleBuilderError("No rule loaded. Call create_rule() first.")
        
        condition = Condition(
            field_id=field_id,
            operator=operator,
            value=value,
        )
        
        self.current_rule.conditions.append(condition)
        self.current_rule.updated_at = datetime.utcnow()
        return condition
    
    def remove_condition(self, index: int) -> bool:
        """Remove a condition by index"""
        if not self.current_rule:
            raise RuleBuilderError("No rule loaded.")
        
        if 0 <= index < len(self.current_rule.conditions):
            self.current_rule.conditions.pop(index)
            self.current_rule.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_condition(
        self,
        index: int,
        field_id: Optional[str] = None,
        operator: Optional[Operator] = None,
        value: Optional[Any] = None,
    ) -> Optional[Condition]:
        """Update a condition"""
        if not self.current_rule:
            raise RuleBuilderError("No rule loaded.")
        
        if 0 <= index < len(self.current_rule.conditions):
            condition = self.current_rule.conditions[index]
            if field_id is not None:
                condition.field_id = field_id
            if operator is not None:
                condition.operator = operator
            if value is not None:
                condition.value = value
            self.current_rule.updated_at = datetime.utcnow()
            return condition
        return None
    
    def get_condition(self, index: int) -> Optional[Condition]:
        """Get a condition by index"""
        if not self.current_rule:
            return None
        if 0 <= index < len(self.current_rule.conditions):
            return self.current_rule.conditions[index]
        return None
    
    def list_conditions(self) -> List[Condition]:
        """List all conditions in the rule"""
        if not self.current_rule:
            return []
        return self.current_rule.conditions
    
    def set_logic(self, logic: LogicOperator) -> LogicOperator:
        """Set the logic operator (AND/OR) for combining conditions"""
        if not self.current_rule:
            raise RuleBuilderError("No rule loaded.")
        self.current_rule.logic = logic
        self.current_rule.updated_at = datetime.utcnow()
        return logic
    
    # ========================================================================
    # ACTION MANAGEMENT
    # ========================================================================
    
    def add_action(
        self,
        action_type: str,
        target: Optional[str] = None,
        value: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RuleAction:
        """Add an action to the rule"""
        if not self.current_rule:
            raise RuleBuilderError("No rule loaded.")
        
        action = RuleAction(
            type=action_type,
            target=target,
            value=value,
            metadata=metadata or {},
        )
        
        self.current_rule.actions.append(action)
        self.current_rule.updated_at = datetime.utcnow()
        return action
    
    def remove_action(self, index: int) -> bool:
        """Remove an action by index"""
        if not self.current_rule:
            raise RuleBuilderError("No rule loaded.")
        
        if 0 <= index < len(self.current_rule.actions):
            self.current_rule.actions.pop(index)
            self.current_rule.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_action(self, index: int) -> Optional[RuleAction]:
        """Get an action by index"""
        if not self.current_rule:
            return None
        if 0 <= index < len(self.current_rule.actions):
            return self.current_rule.actions[index]
        return None
    
    def list_actions(self) -> List[RuleAction]:
        """List all actions in the rule"""
        if not self.current_rule:
            return []
        return self.current_rule.actions
    
    # ========================================================================
    # RULE EXECUTION AND TESTING
    # ========================================================================
    
    def evaluate(self, data: Dict[str, Any]) -> bool:
        """Evaluate if rule conditions match the given data"""
        if not self.current_rule or not self.current_rule.conditions:
            return False
        
        results = []
        for condition in self.current_rule.conditions:
            result = self._evaluate_condition(condition, data)
            results.append(result)
        
        # Combine results based on logic operator
        if self.current_rule.logic == LogicOperator.AND:
            return all(results)
        else:  # OR
            return any(results)
    
    def _evaluate_condition(self, condition: Condition, data: Dict[str, Any]) -> bool:
        """Evaluate a single condition against data"""
        if condition.field_id not in data:
            return False
        
        field_value = data[condition.field_id]
        target_value = condition.value
        
        # Operator evaluation
        if condition.operator == Operator.EQUALS:
            return field_value == target_value
        elif condition.operator == Operator.NOT_EQUALS:
            return field_value != target_value
        elif condition.operator == Operator.GREATER_THAN:
            return field_value > target_value
        elif condition.operator == Operator.LESS_THAN:
            return field_value < target_value
        elif condition.operator == Operator.GREATER_EQUAL:
            return field_value >= target_value
        elif condition.operator == Operator.LESS_EQUAL:
            return field_value <= target_value
        elif condition.operator == Operator.CONTAINS:
            return target_value in str(field_value)
        elif condition.operator == Operator.NOT_CONTAINS:
            return target_value not in str(field_value)
        elif condition.operator == Operator.IN_LIST:
            return field_value in target_value if isinstance(target_value, list) else False
        elif condition.operator == Operator.NOT_IN_LIST:
            return field_value not in target_value if isinstance(target_value, list) else True
        elif condition.operator == Operator.STARTS_WITH:
            return str(field_value).startswith(str(target_value))
        elif condition.operator == Operator.ENDS_WITH:
            return str(field_value).endswith(str(target_value))
        
        return False
    
    def execute_actions(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute rule actions if conditions match"""
        if not self.evaluate(data):
            return []
        
        executed = []
        for action in self.current_rule.actions:
            result = {
                "type": action.type,
                "target": action.target,
                "value": action.value,
                "executed": True,
                "timestamp": datetime.utcnow().isoformat(),
            }
            executed.append(result)
        
        return executed
    
    def test_rule(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test rule against sample data"""
        if not self.current_rule:
            raise RuleBuilderError("No rule loaded.")
        
        matched = self.evaluate(test_data)
        actions_executed = self.execute_actions(test_data) if matched else []
        
        return {
            "rule_id": self.current_rule.id,
            "matched": matched,
            "conditions_evaluated": len(self.current_rule.conditions),
            "logic_operator": self.current_rule.logic.value,
            "actions_executed": len(actions_executed),
            "actions": actions_executed,
            "test_data": test_data,
        }
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    
    def validate_rule(self) -> Dict[str, Any]:
        """Validate the current rule configuration"""
        if not self.current_rule:
            return {"valid": False, "errors": ["No rule loaded"]}
        
        errors = []
        warnings = []
        
        # Check basic properties
        if not self.current_rule.name:
            errors.append("Rule name is required")
        
        # Check conditions
        if not self.current_rule.conditions:
            errors.append("Rule must have at least one condition")
        else:
            for i, condition in enumerate(self.current_rule.conditions):
                if not condition.field_id:
                    errors.append(f"Condition {i} missing field_id")
                if not condition.operator:
                    errors.append(f"Condition {i} missing operator")
        
        # Check actions
        if not self.current_rule.actions:
            errors.append("Rule must have at least one action")
        else:
            for i, action in enumerate(self.current_rule.actions):
                if not action.type:
                    errors.append(f"Action {i} missing type")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "condition_count": len(self.current_rule.conditions),
            "action_count": len(self.current_rule.actions),
        }
    
    # ========================================================================
    # CONVERSION TO WORKFLOW RULE
    # ========================================================================
    
    def to_workflow_rule(self) -> WorkflowRule:
        """Convert draft to a workflow rule"""
        if not self.current_rule:
            raise RuleBuilderError("No rule loaded.")
        
        return WorkflowRule(
            id=self.current_rule.id,
            name=self.current_rule.name,
            enabled=self.current_rule.enabled,
            description=self.current_rule.description,
            conditions=self.current_rule.conditions,
            logic=self.current_rule.logic,
            actions=self.current_rule.actions,
            priority=self.current_rule.priority,
        )
