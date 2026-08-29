"""Phase 2 Constants and Pre-built Templates"""

from .schemas import (
    WorkflowTemplate,
    WorkflowField,
    OutputFieldDef,
    OutputSchema,
    FieldType,
    FieldValidation,
)
from datetime import datetime

# ============================================================================
# TEMPLATE CATALOG - Pre-built workflow templates
# ============================================================================

TEMPLATE_8D_INVESTIGATION = WorkflowTemplate(
    id="template-8d",
    name="8D Quality Investigation",
    description="Structured 8D problem-solving for manufacturing quality incidents",
    category="8d",
    version="1.0",
    form_fields=[
        WorkflowField(
            id="incident_id",
            label="Incident ID",
            field_type=FieldType.TEXT,
            validation=FieldValidation(required=True, max_length=50),
            section="Incident Details",
            order=1,
        ),
        WorkflowField(
            id="incident_date",
            label="Incident Date",
            field_type=FieldType.DATE,
            validation=FieldValidation(required=True),
            section="Incident Details",
            order=2,
        ),
        WorkflowField(
            id="plant",
            label="Plant",
            field_type=FieldType.TEXT,
            validation=FieldValidation(required=True),
            section="Incident Details",
            order=3,
        ),
        WorkflowField(
            id="severity",
            label="Severity Level",
            field_type=FieldType.SELECT,
            options=[
                {"value": "low", "label": "Low"},
                {"value": "medium", "label": "Medium"},
                {"value": "high", "label": "High"},
                {"value": "critical", "label": "Critical"},
            ],
            validation=FieldValidation(required=True),
            section="Incident Details",
            order=4,
        ),
        WorkflowField(
            id="defect_statement",
            label="Defect Statement",
            field_type=FieldType.TEXTAREA,
            validation=FieldValidation(required=True, min_length=10),
            help_text="Describe the observed defect clearly",
            section="Problem Description",
            order=5,
        ),
        WorkflowField(
            id="quantity_affected",
            label="Quantity Affected",
            field_type=FieldType.NUMBER,
            validation=FieldValidation(required=True, min_value=0),
            section="Problem Description",
            order=6,
        ),
    ],
    output_schema=OutputSchema(
        id="schema-8d",
        name="8D Investigation Output",
        fields=[
            OutputFieldDef(id="D1_team", name="D1: Team", field_type=FieldType.TEXT),
            OutputFieldDef(id="D2_problem", name="D2: Problem Statement", field_type=FieldType.TEXTAREA),
            OutputFieldDef(id="D3_containment", name="D3: Containment", field_type=FieldType.TEXTAREA, repeatable=True),
            OutputFieldDef(id="D4_root_cause", name="D4: Root Cause", field_type=FieldType.TEXTAREA),
            OutputFieldDef(id="D5_actions", name="D5: Corrective Actions", field_type=FieldType.TEXTAREA, repeatable=True),
            OutputFieldDef(id="D6_prevention", name="D6: Prevention", field_type=FieldType.TEXTAREA),
            OutputFieldDef(id="D7_verification", name="D7: Verification", field_type=FieldType.TEXTAREA),
            OutputFieldDef(id="D8_closure", name="D8: Closure", field_type=FieldType.TEXTAREA),
        ],
    ),
)

TEMPLATE_EQUIPMENT_FAULT = WorkflowTemplate(
    id="template-equipment-fault",
    name="Equipment Fault Triage",
    description="Classify and route equipment failures for diagnosis and repair",
    category="equipment_fault",
    version="1.0",
    form_fields=[
        WorkflowField(
            id="fault_id",
            label="Fault ID",
            field_type=FieldType.TEXT,
            validation=FieldValidation(required=True),
            section="Fault Details",
            order=1,
        ),
        WorkflowField(
            id="asset_name",
            label="Asset / Equipment Name",
            field_type=FieldType.TEXT,
            validation=FieldValidation(required=True),
            section="Fault Details",
            order=2,
        ),
        WorkflowField(
            id="fault_description",
            label="Fault Description",
            field_type=FieldType.TEXTAREA,
            validation=FieldValidation(required=True, min_length=10),
            section="Fault Details",
            order=3,
        ),
        WorkflowField(
            id="fault_priority",
            label="Priority",
            field_type=FieldType.SELECT,
            options=[
                {"value": "low", "label": "Low"},
                {"value": "medium", "label": "Medium"},
                {"value": "high", "label": "High"},
                {"value": "critical", "label": "Critical - Production Stop"},
            ],
            validation=FieldValidation(required=True),
            section="Fault Details",
            order=4,
        ),
    ],
    output_schema=OutputSchema(
        id="schema-fault",
        name="Equipment Fault Output",
        fields=[
            OutputFieldDef(id="category", name="Fault Category", field_type=FieldType.TEXT),
            OutputFieldDef(id="likely_causes", name="Likely Causes", field_type=FieldType.TEXTAREA, repeatable=True),
            OutputFieldDef(id="diagnostic_checks", name="Diagnostic Checks", field_type=FieldType.TEXTAREA, repeatable=True),
            OutputFieldDef(id="recommended_route", name="Recommended Route", field_type=FieldType.TEXT),
            OutputFieldDef(id="assigned_role", name="Assigned To Role", field_type=FieldType.TEXT),
        ],
    ),
)

TEMPLATE_NONCONFORMANCE = WorkflowTemplate(
    id="template-nonconformance",
    name="Nonconformance Report",
    description="Document and process product and process nonconformances",
    category="nonconformance",
    version="1.0",
    form_fields=[
        WorkflowField(
            id="ncr_number",
            label="NCR Number",
            field_type=FieldType.TEXT,
            validation=FieldValidation(required=True),
            section="NCR Details",
            order=1,
        ),
        WorkflowField(
            id="part_number",
            label="Part Number",
            field_type=FieldType.TEXT,
            validation=FieldValidation(required=True),
            section="NCR Details",
            order=2,
        ),
        WorkflowField(
            id="nonconformance_type",
            label="Type",
            field_type=FieldType.SELECT,
            options=[
                {"value": "product", "label": "Product"},
                {"value": "process", "label": "Process"},
                {"value": "documentation", "label": "Documentation"},
            ],
            validation=FieldValidation(required=True),
            section="NCR Details",
            order=3,
        ),
    ],
    output_schema=OutputSchema(
        id="schema-ncr",
        name="Nonconformance Output",
        fields=[
            OutputFieldDef(id="description", name="Description", field_type=FieldType.TEXTAREA),
            OutputFieldDef(id="disposition", name="Disposition", field_type=FieldType.TEXT),
            OutputFieldDef(id="corrective_action", name="Corrective Action", field_type=FieldType.TEXTAREA),
        ],
    ),
)

# Catalog of all available templates
TEMPLATE_CATALOG = {
    "template-8d": TEMPLATE_8D_INVESTIGATION,
    "template-equipment-fault": TEMPLATE_EQUIPMENT_FAULT,
    "template-nonconformance": TEMPLATE_NONCONFORMANCE,
}

# ============================================================================
# DEFAULT CONFIGURATIONS
# ============================================================================

DEFAULT_VALIDATION_RULES = {
    "text_field": FieldValidation(required=True, max_length=100),
    "textarea_field": FieldValidation(required=True, min_length=10, max_length=2000),
    "number_field": FieldValidation(required=True, min_value=0),
    "email_field": FieldValidation(
        required=True,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        custom_message="Please enter a valid email address",
    ),
}

DEFAULT_PROMPT_SETTINGS = {
    "temperature": 0.2,
    "max_tokens": 2000,
    "model": "gemini-3.6-flash",
}

# Field type limitations
FIELD_TYPE_LIMITS = {
    FieldType.TEXT: {"max_length": 500},
    FieldType.TEXTAREA: {"max_length": 5000},
    FieldType.NUMBER: {"min_value": -1e10, "max_value": 1e10},
    FieldType.SELECT: {"max_options": 100},
    FieldType.MULTISELECT: {"max_options": 100},
}

# Phase 2 version and metadata
PHASE_2_VERSION = "0.1.0"
PHASE_2_EXIT_CRITERIA = """
Phase 2 Exit Criteria:
- An authorized user can create a new workflow from a template without editing Python
- Form builder supports all field types with validation
- Rule builder handles routing, approval, categorization
- Prompt templates are versioned and approvable
- Output schemas are definable and exportable
- Configuration packages can be imported/exported as versioned JSON
"""
