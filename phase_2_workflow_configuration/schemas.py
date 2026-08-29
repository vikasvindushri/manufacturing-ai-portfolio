"""Phase 2 Core Data Models and Schemas for Workflow Configuration"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from enum import Enum
from datetime import datetime

# ============================================================================
# FIELD TYPES AND DEFINITIONS
# ============================================================================

class FieldType(str, Enum):
    """Supported field types in workflow forms"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FILE = "file"
    EMAIL = "email"
    PHONE = "phone"

class FieldValidation(BaseModel):
    """Validation rules for a field"""
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None  # regex pattern
    allowed_values: Optional[List[str]] = None
    custom_message: Optional[str] = None

class WorkflowField(BaseModel):
    """Definition of a single form field in a workflow"""
    id: str = Field(..., description="Unique field identifier")
    label: str = Field(..., description="User-facing field label")
    field_type: FieldType
    description: Optional[str] = None
    placeholder: Optional[str] = None
    default_value: Optional[Any] = None
    validation: FieldValidation = Field(default_factory=lambda: FieldValidation())
    options: Optional[List[Dict[str, str]]] = None  # for select/radio/multiselect
    help_text: Optional[str] = None
    section: str = "General"  # organize fields into sections
    order: int = 0  # display order
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ============================================================================
# RULE DEFINITIONS
# ============================================================================

class Operator(str, Enum):
    """Comparison operators for rules"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"

class Condition(BaseModel):
    """A single condition in a rule"""
    field_id: str = Field(..., description="Field to evaluate")
    operator: Operator
    value: Any = Field(..., description="Value to compare against")

class LogicOperator(str, Enum):
    """Logical operators for combining conditions"""
    AND = "and"
    OR = "or"

class RuleAction(BaseModel):
    """Action to take when a rule matches"""
    type: Literal["route", "require_approval", "set_category", "set_severity", "set_field_value", "show_message"]
    target: Optional[str] = None  # e.g., role name, field name, message text
    value: Optional[Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowRule(BaseModel):
    """A rule for workflow routing, approval, or categorization"""
    id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Human-readable rule name")
    enabled: bool = True
    description: Optional[str] = None
    conditions: List[Condition] = Field(..., min_items=1)
    logic: LogicOperator = LogicOperator.AND
    actions: List[RuleAction] = Field(..., min_items=1)
    priority: int = 0  # higher priority rules evaluated first
    order: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ============================================================================
# PROMPT TEMPLATE DEFINITIONS
# ============================================================================

class PromptTemplate(BaseModel):
    """LLM prompt template with versioning and approval"""
    id: str = Field(..., description="Unique template identifier")
    name: str
    description: Optional[str] = None
    purpose: Literal["quality_review", "triage_review", "knowledge_synthesis", "custom"]
    version: str = Field(default="1.0", description="Semantic version")
    status: Literal["draft", "approved", "deprecated"] = "draft"
    system_instruction: str = Field(..., description="System prompt for LLM")
    user_prompt_template: str = Field(..., description="User prompt with {field} placeholders")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2000, ge=100)
    model: str = Field(default="gemini-3.6-flash")
    input_variables: List[str] = Field(default_factory=list, description="Variables used in template")
    output_schema: Optional[Dict[str, Any]] = None  # Pydantic schema for structured output
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ============================================================================
# OUTPUT SCHEMA DEFINITIONS
# ============================================================================

class OutputFieldDef(BaseModel):
    """Definition of an output field"""
    id: str
    name: str
    field_type: FieldType
    description: Optional[str] = None
    required: bool = True
    repeatable: bool = False  # for arrays
    nested_fields: Optional[List['OutputFieldDef']] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

OutputFieldDef.model_rebuild()

class OutputSchema(BaseModel):
    """Schema for workflow output records"""
    id: str = Field(..., description="Unique schema identifier")
    name: str
    description: Optional[str] = None
    version: str = Field(default="1.0")
    status: Literal["draft", "active", "archived"] = "draft"
    fields: List[OutputFieldDef] = Field(..., min_items=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# WORKFLOW TEMPLATE DEFINITIONS
# ============================================================================

class WorkflowTemplate(BaseModel):
    """Pre-built workflow template"""
    id: str
    name: str
    description: str
    category: Literal["8d", "nonconformance", "equipment_fault", "audit", "knowledge_search", "custom"]
    version: str = "1.0"
    status: Literal["active", "archived"] = "active"
    form_fields: List[WorkflowField]
    rules: List[WorkflowRule] = Field(default_factory=list)
    prompt_templates: List[PromptTemplate] = Field(default_factory=list)
    output_schema: OutputSchema
    documentation: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ============================================================================
# WORKFLOW CONFIGURATION
# ============================================================================

class WorkflowConfiguration(BaseModel):
    """Complete workflow configuration (user-created from template or custom)"""
    id: str = Field(..., description="Unique configuration ID")
    name: str
    description: Optional[str] = None
    template_id: Optional[str] = None  # source template, if created from one
    version: str = "1.0"
    status: Literal["draft", "testing", "active", "archived"] = "draft"
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Configuration components
    form_fields: List[WorkflowField] = Field(default_factory=list)
    rules: List[WorkflowRule] = Field(default_factory=list)
    prompt_templates: List[PromptTemplate] = Field(default_factory=list)
    output_schema: Optional[OutputSchema] = None
    
    # Metadata and governance
    owner_role: str = "workflow_owner"
    requires_approval: bool = True
    approval_roles: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "config-001",
                "name": "Quality Investigation",
                "template_id": "template-8d",
                "status": "active",
                "created_by": "quality-team"
            }
        }

# ============================================================================
# CONFIGURATION PACKAGE (IMPORT/EXPORT)
# ============================================================================

class ConfigurationPackage(BaseModel):
    """Versioned configuration package for import/export"""
    id: str = Field(..., description="Package identifier")
    name: str
    description: Optional[str] = None
    version: str = Field(..., description="Package version (semantic)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    
    # Configuration contents
    workflows: List[WorkflowConfiguration]
    templates: List[WorkflowTemplate] = Field(default_factory=list)
    prompt_templates: List[PromptTemplate] = Field(default_factory=list)
    
    # Package metadata
    tags: List[str] = Field(default_factory=list)
    dependencies: Dict[str, str] = Field(default_factory=dict)  # external dependencies and versions
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConfigurationExport(BaseModel):
    """Export format for workflows"""
    export_id: str
    export_date: datetime = Field(default_factory=datetime.utcnow)
    format_version: str = "1.0"
    package: ConfigurationPackage
    checksums: Dict[str, str] = Field(default_factory=dict)  # For integrity verification
