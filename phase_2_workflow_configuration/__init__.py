"""Phase 2: Workflow Configuration System

Phase 2 enables authorized users to configure common manufacturing workflows
using point-and-click controls without editing Python code.

Components:
- Form Builder: Configure incident, document, and fault intake fields
- Rule Builder: Configure routing, approval, categorization
- Prompt Editor: Create and version LLM prompts
- Output Schema Designer: Define output field types
- Template Catalog: Pre-built templates for common workflows
- Configuration Management: Import/export versioned packages
"""

from .schemas import (
    FieldType,
    FieldValidation,
    WorkflowField,
    Operator,
    Condition,
    LogicOperator,
    RuleAction,
    WorkflowRule,
    PromptTemplate,
    OutputFieldDef,
    OutputSchema,
    WorkflowTemplate,
    WorkflowConfiguration,
    ConfigurationPackage,
    ConfigurationExport,
)

__all__ = [
    "FieldType",
    "FieldValidation",
    "WorkflowField",
    "Operator",
    "Condition",
    "LogicOperator",
    "RuleAction",
    "WorkflowRule",
    "PromptTemplate",
    "OutputFieldDef",
    "OutputSchema",
    "WorkflowTemplate",
    "WorkflowConfiguration",
    "ConfigurationPackage",
    "ConfigurationExport",
]

__version__ = "0.1.0"
__phase__ = "Phase 2: Workflow Configuration"
