"""Phase 2 Form Builder - Create and manage workflow intake forms"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from phase_2_workflow_configuration.schemas import (
    WorkflowField,
    FieldType,
    FieldValidation,
)

class FormBuilderError(Exception):
    """Form builder operation error"""
    pass

class FormField(BaseModel):
    """A field in a form being built"""
    id: str
    label: str
    field_type: FieldType
    description: Optional[str] = None
    placeholder: Optional[str] = None
    default_value: Optional[Any] = None
    validation: FieldValidation
    options: Optional[List[Dict[str, str]]] = None
    help_text: Optional[str] = None
    section: str = "General"
    order: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FormSection(BaseModel):
    """Logical section of form fields"""
    name: str
    description: Optional[str] = None
    fields: List[FormField] = Field(default_factory=list)
    order: int = 0
    collapsed_by_default: bool = False

class FormDraft(BaseModel):
    """Form under construction"""
    id: str
    workflow_id: str
    name: str
    description: Optional[str] = None
    sections: List[FormSection] = Field(default_factory=list)
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    locked: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FormBuilder:
    """Builder for creating and editing workflow intake forms"""
    
    def __init__(self):
        self.current_form: Optional[FormDraft] = None
    
    # ========================================================================
    # FORM LIFECYCLE
    # ========================================================================
    
    def create_form(self, workflow_id: str, form_id: str, name: str, created_by: str) -> FormDraft:
        """Create a new form draft"""
        self.current_form = FormDraft(
            id=form_id,
            workflow_id=workflow_id,
            name=name,
            created_by=created_by,
        )
        return self.current_form
    
    def load_form(self, form_draft: FormDraft) -> FormDraft:
        """Load an existing form draft for editing"""
        if form_draft.locked:
            raise FormBuilderError(f"Form {form_draft.id} is locked and cannot be edited")
        self.current_form = form_draft
        return self.current_form
    
    def get_form(self) -> Optional[FormDraft]:
        """Get the current form being edited"""
        return self.current_form
    
    # ========================================================================
    # SECTION MANAGEMENT
    # ========================================================================
    
    def add_section(self, section_name: str, description: Optional[str] = None) -> FormSection:
        """Add a new section to the form"""
        if not self.current_form:
            raise FormBuilderError("No form loaded. Call create_form() first.")
        
        section = FormSection(
            name=section_name,
            description=description,
            order=len(self.current_form.sections),
        )
        self.current_form.sections.append(section)
        self.current_form.updated_at = datetime.utcnow()
        return section
    
    def remove_section(self, section_name: str) -> bool:
        """Remove a section from the form"""
        if not self.current_form:
            raise FormBuilderError("No form loaded.")
        
        before = len(self.current_form.sections)
        self.current_form.sections = [
            s for s in self.current_form.sections if s.name != section_name
        ]
        removed = len(self.current_form.sections) < before
        if removed:
            self.current_form.updated_at = datetime.utcnow()
        return removed
    
    def get_section(self, section_name: str) -> Optional[FormSection]:
        """Get a section by name"""
        if not self.current_form:
            return None
        return next(
            (s for s in self.current_form.sections if s.name == section_name),
            None,
        )
    
    # ========================================================================
    # FIELD MANAGEMENT
    # ========================================================================
    
    def add_field(
        self,
        section_name: str,
        field_id: str,
        label: str,
        field_type: FieldType,
        **kwargs,
    ) -> FormField:
        """Add a field to a section"""
        if not self.current_form:
            raise FormBuilderError("No form loaded.")
        
        section = self.get_section(section_name)
        if not section:
            raise FormBuilderError(f"Section '{section_name}' not found.")
        
        # Validate field_id uniqueness
        all_field_ids = {f.id for s in self.current_form.sections for f in s.fields}
        if field_id in all_field_ids:
            raise FormBuilderError(f"Field ID '{field_id}' already exists.")
        
        # Extract and validate kwargs
        validation = kwargs.pop("validation", FieldValidation())
        options = kwargs.pop("options", None)
        help_text = kwargs.pop("help_text", None)
        placeholder = kwargs.pop("placeholder", None)
        default_value = kwargs.pop("default_value", None)
        order = kwargs.pop("order", len(section.fields))
        
        field = FormField(
            id=field_id,
            label=label,
            field_type=field_type,
            validation=validation,
            options=options,
            help_text=help_text,
            placeholder=placeholder,
            default_value=default_value,
            section=section_name,
            order=order,
            **kwargs,
        )
        
        section.fields.append(field)
        section.fields.sort(key=lambda f: f.order)
        self.current_form.updated_at = datetime.utcnow()
        return field
    
    def remove_field(self, section_name: str, field_id: str) -> bool:
        """Remove a field from a section"""
        if not self.current_form:
            raise FormBuilderError("No form loaded.")
        
        section = self.get_section(section_name)
        if not section:
            return False
        
        before = len(section.fields)
        section.fields = [f for f in section.fields if f.id != field_id]
        removed = len(section.fields) < before
        if removed:
            self.current_form.updated_at = datetime.utcnow()
        return removed
    
    def update_field(
        self, section_name: str, field_id: str, **updates
    ) -> Optional[FormField]:
        """Update field properties"""
        if not self.current_form:
            raise FormBuilderError("No form loaded.")
        
        section = self.get_section(section_name)
        if not section:
            return None
        
        field = next((f for f in section.fields if f.id == field_id), None)
        if not field:
            return None
        
        # Update allowed properties
        allowed_updates = {
            "label", "description", "placeholder", "default_value",
            "validation", "options", "help_text", "order", "metadata"
        }
        
        for key, value in updates.items():
            if key in allowed_updates:
                setattr(field, key, value)
        
        self.current_form.updated_at = datetime.utcnow()
        return field
    
    def get_field(self, section_name: str, field_id: str) -> Optional[FormField]:
        """Get a specific field"""
        section = self.get_section(section_name)
        if not section:
            return None
        return next((f for f in section.fields if f.id == field_id), None)
    
    def list_fields(self, section_name: Optional[str] = None) -> List[FormField]:
        """List all fields, optionally filtered by section"""
        if not self.current_form:
            return []
        
        if section_name:
            section = self.get_section(section_name)
            return section.fields if section else []
        
        fields = []
        for section in self.current_form.sections:
            fields.extend(section.fields)
        return sorted(fields, key=lambda f: (f.section, f.order))
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    
    def validate_form(self) -> Dict[str, Any]:
        """Validate the current form configuration"""
        if not self.current_form:
            return {"valid": False, "errors": ["No form loaded"]}
        
        errors = []
        warnings = []
        
        # Check for empty sections
        if not self.current_form.sections:
            errors.append("Form has no sections")
        
        # Check each section
        for section in self.current_form.sections:
            if not section.fields:
                warnings.append(f"Section '{section.name}' has no fields")
            
            # Check for duplicate field IDs
            field_ids = [f.id for f in section.fields]
            duplicates = [fid for fid in set(field_ids) if field_ids.count(fid) > 1]
            if duplicates:
                errors.append(f"Duplicate field IDs in section '{section.name}': {duplicates}")
            
            # Validate field configurations
            for field in section.fields:
                field_errors = self._validate_field(field)
                errors.extend(field_errors)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "field_count": sum(len(s.fields) for s in self.current_form.sections),
            "section_count": len(self.current_form.sections),
        }
    
    def _validate_field(self, field: FormField) -> List[str]:
        """Validate a single field configuration"""
        errors = []
        
        if not field.id:
            errors.append(f"Field missing ID")
        if not field.label:
            errors.append(f"Field {field.id} missing label")
        
        # Validate options for select fields
        if field.field_type in [FieldType.SELECT, FieldType.RADIO, FieldType.MULTISELECT]:
            if not field.options:
                errors.append(f"Field {field.id} ({field.field_type}) requires options")
        
        # Validate validation rules
        if field.validation.pattern:
            try:
                import re
                re.compile(field.validation.pattern)
            except Exception as e:
                errors.append(f"Field {field.id} has invalid regex pattern: {e}")
        
        return errors
    
    # ========================================================================
    # EXPORT AND CONVERSION
    # ========================================================================
    
    def to_workflow_fields(self) -> List[WorkflowField]:
        """Convert form to workflow field definitions"""
        if not self.current_form:
            return []
        
        workflow_fields = []
        order = 0
        
        for section in self.current_form.sections:
            for field in section.fields:
                workflow_field = WorkflowField(
                    id=field.id,
                    label=field.label,
                    field_type=field.field_type,
                    description=field.description,
                    placeholder=field.placeholder,
                    default_value=field.default_value,
                    validation=field.validation,
                    options=field.options,
                    help_text=field.help_text,
                    section=field.section,
                    order=order,
                    metadata=field.metadata,
                )
                workflow_fields.append(workflow_field)
                order += 1
        
        return workflow_fields
    
    def get_json_schema(self) -> Dict[str, Any]:
        """Export form as JSON schema for frontend consumption"""
        if not self.current_form:
            return {}
        
        sections = []
        for section in self.current_form.sections:
            fields = [
                {
                    "id": f.id,
                    "label": f.label,
                    "type": f.field_type.value,
                    "description": f.description,
                    "placeholder": f.placeholder,
                    "defaultValue": f.default_value,
                    "options": f.options,
                    "helpText": f.help_text,
                    "validation": {
                        "required": f.validation.required,
                        "minLength": f.validation.min_length,
                        "maxLength": f.validation.max_length,
                        "minValue": f.validation.min_value,
                        "maxValue": f.validation.max_value,
                        "pattern": f.validation.pattern,
                    },
                }
                for f in section.fields
            ]
            
            sections.append({
                "name": section.name,
                "description": section.description,
                "fields": fields,
                "order": section.order,
                "collapsedByDefault": section.collapsed_by_default,
            })
        
        return {
            "id": self.current_form.id,
            "workflowId": self.current_form.workflow_id,
            "name": self.current_form.name,
            "description": self.current_form.description,
            "sections": sections,
            "createdAt": self.current_form.created_at.isoformat(),
            "updatedAt": self.current_form.updated_at.isoformat(),
        }
