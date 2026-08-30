"""Versioned, safe workflow-definition domain model."""
from __future__ import annotations

import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{2,63}$")
SECRET_KEYS = {
    "api_key", "apikey", "password", "secret", "token", "private_key",
    "gemini_api_key", "google_api_key",
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class LifecycleStatus(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class FieldType(str, Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    SELECT = "select"
    MULTISELECT = "multiselect"


class RuleOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN = "in"


def _valid_id(value: str, label: str) -> str:
    if not ID_PATTERN.fullmatch(value):
        raise ValueError(f"{label} must match {ID_PATTERN.pattern}")
    return value


def _find_secret_paths(value: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}" if path else str(key)
            if str(key).lower() in SECRET_KEYS:
                found.append(child)
            found.extend(_find_secret_paths(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_find_secret_paths(item, f"{path}[{index}]"))
    return found


class WorkflowMetadata(StrictModel):
    workflow_id: str
    name: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=1000)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    owner: str = Field(min_length=2, max_length=120)
    status: LifecycleStatus = LifecycleStatus.DRAFT
    definition_version: str = "1.0"
    tags: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def validate_identifier(self):
        self.workflow_id = _valid_id(self.workflow_id, "workflow_id")
        return self


class FieldDefinition(StrictModel):
    field_id: str
    label: str = Field(min_length=1, max_length=120)
    field_type: FieldType
    required: bool = False
    help_text: str | None = Field(default=None, max_length=500)
    default: Any = None
    options: list[str] = Field(default_factory=list)
    sensitive: bool = False

    @model_validator(mode="after")
    def validate_field(self):
        self.field_id = _valid_id(self.field_id, "field_id")
        selection = self.field_type in {FieldType.SELECT, FieldType.MULTISELECT}
        if selection and not self.options:
            raise ValueError("select and multiselect fields require options")
        if not selection and self.options:
            raise ValueError("options are only valid for select and multiselect fields")
        return self


class RuleDefinition(StrictModel):
    rule_id: str
    field_id: str
    operator: RuleOperator
    value: Any
    message: str = Field(min_length=3, max_length=300)

    @model_validator(mode="after")
    def validate_identifiers(self):
        self.rule_id = _valid_id(self.rule_id, "rule_id")
        self.field_id = _valid_id(self.field_id, "field_id")
        return self


class ApprovalPolicy(StrictModel):
    required: bool = True
    minimum_approvals: int = Field(default=1, ge=1, le=10)
    allowed_roles: list[str] = Field(default_factory=lambda: ["workflow_reviewer"])
    rationale_required: bool = True


class WorkflowDefinition(StrictModel):
    metadata: WorkflowMetadata
    fields: list[FieldDefinition] = Field(min_length=1, max_length=100)
    rules: list[RuleDefinition] = Field(default_factory=list, max_length=200)
    approval: ApprovalPolicy = Field(default_factory=ApprovalPolicy)
    extensions: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_workflow(self):
        field_ids = [field.field_id for field in self.fields]
        if len(field_ids) != len(set(field_ids)):
            raise ValueError("field_id values must be unique")
        rule_ids = [rule.rule_id for rule in self.rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError("rule_id values must be unique")
        unknown = sorted({rule.field_id for rule in self.rules} - set(field_ids))
        if unknown:
            raise ValueError(f"rules reference unknown fields: {unknown}")
        if not self.approval.required:
            raise ValueError("human approval is mandatory for governed workflows")
        secret_paths = _find_secret_paths(self.model_dump(mode="json"))
        if secret_paths:
            raise ValueError(f"workflow definitions cannot contain secrets: {secret_paths}")
        return self
