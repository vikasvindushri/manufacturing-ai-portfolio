"""Phase 2 Form Builder UI - Streamlit components for form configuration"""
import streamlit as st
from typing import Optional, List, Dict, Any
from phase_2_workflow_configuration.form_builder import FormBuilder, FormDraft, FormField
from phase_2_workflow_configuration.schemas import FieldType, FieldValidation

class FormBuilderUI:
    """Streamlit UI for building workflow forms"""
    
    def __init__(self):
        self.builder = FormBuilder()
        if "form_builder_session" not in st.session_state:
            st.session_state.form_builder_session = {"form": None}
    
    # ========================================================================
    # MAIN UI COMPONENTS
    # ========================================================================
    
    def render_form_list(self, forms: List[FormDraft]) -> Optional[str]:
        """Display list of existing forms with selection"""
        st.subheader("📋 Available Forms")
        
        if not forms:
            st.info("No forms found. Create a new one to get started.")
            return None
        
        form_options = {f.name: f.id for f in forms}
        selected_name = st.selectbox(
            "Select a form to edit",
            options=list(form_options.keys()),
            key="form_selection",
        )
        
        return form_options.get(selected_name)
    
    def render_form_creation(self) -> Optional[FormDraft]:
        """UI for creating a new form"""
        st.subheader("➕ Create New Form")
        
        col1, col2 = st.columns(2)
        workflow_id = col1.text_input("Workflow ID *", key="new_form_workflow_id")
        form_name = col2.text_input("Form Name *", key="new_form_name")
        
        form_desc = st.text_area(
            "Form Description",
            placeholder="Optional description of this form",
            key="new_form_desc",
            height=80,
        )
        
        if st.button("✅ Create Form", type="primary", use_container_width=True):
            if not workflow_id or not form_name:
                st.error("Workflow ID and Form Name are required.")
                return None
            
            form = self.builder.create_form(
                workflow_id=workflow_id,
                form_id=f"form-{workflow_id}-{form_name.lower().replace(' ', '_')}",
                name=form_name,
                created_by="current_user",  # TODO: get from session
            )
            form.description = form_desc
            st.session_state.form_builder_session["form"] = form
            st.success(f"✅ Form '{form_name}' created!")
            st.rerun()
        
        return None
    
    def render_form_editor(self, form: FormDraft) -> FormDraft:
        """Main form editing interface"""
        st.subheader(f"✏️ Editing: {form.name}")
        
        # Form info
        with st.expander("📝 Form Details", expanded=False):
            form.name = st.text_input("Form Name", value=form.name)
            form.description = st.text_area("Description", value=form.description or "")
        
        # Tabs for different editing modes
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📋 Sections & Fields", "🔍 Validation", "👁️ Preview", "💾 Export"]
        )
        
        with tab1:
            self._render_sections_editor(form)
        
        with tab2:
            self._render_validation_view(form)
        
        with tab3:
            self._render_preview(form)
        
        with tab4:
            self._render_export(form)
        
        return form
    
    def _render_sections_editor(self, form: FormDraft) -> None:
        """Editor for form sections and fields"""
        self.builder.current_form = form
        
        # Add new section
        st.markdown("### Add New Section")
        col1, col2 = st.columns([2, 1])
        section_name = col1.text_input("Section Name", key="new_section_name")
        if col2.button("➕ Add", use_container_width=True):
            if section_name:
                self.builder.add_section(section_name)
                st.success(f"Section '{section_name}' added!")
                st.rerun()
            else:
                st.error("Section name is required.")
        
        st.divider()
        
        # Edit existing sections
        if not form.sections:
            st.info("No sections yet. Add one above to get started.")
            return
        
        for section in form.sections:
            with st.expander(f"📂 {section.name}", expanded=True):
                # Section settings
                col1, col2 = st.columns(2)
                section.description = col1.text_input(
                    "Section Description",
                    value=section.description or "",
                    key=f"section_desc_{section.name}",
                )
                section.collapsed_by_default = col2.checkbox(
                    "Collapsed by default",
                    value=section.collapsed_by_default,
                    key=f"section_collapsed_{section.name}",
                )
                
                # Remove section button
                if st.button(
                    "🗑️ Remove Section",
                    key=f"remove_section_{section.name}",
                    use_container_width=True,
                ):
                    self.builder.remove_section(section.name)
                    st.success(f"Section '{section.name}' removed!")
                    st.rerun()
                
                st.divider()
                
                # Add field to section
                st.markdown("#### Add Field")
                self._render_field_creator(section.name)
                
                st.divider()
                
                # Edit existing fields
                if section.fields:
                    st.markdown("#### Fields in this section")
                    for field in section.fields:
                        self._render_field_editor(section.name, field)
                else:
                    st.info("No fields in this section yet.")
    
    def _render_field_creator(self, section_name: str) -> None:
        """UI for adding a new field to a section"""
        col1, col2, col3 = st.columns(3)
        field_id = col1.text_input("Field ID *", key=f"field_id_{section_name}")
        label = col2.text_input("Label *", key=f"field_label_{section_name}")
        field_type = col3.selectbox(
            "Type *",
            options=[ft.value for ft in FieldType],
            key=f"field_type_{section_name}",
        )
        
        col1, col2 = st.columns(2)
        placeholder = col1.text_input("Placeholder", key=f"field_placeholder_{section_name}")
        description = col2.text_area("Description", key=f"field_desc_{section_name}", height=60)
        
        col1, col2 = st.columns(2)
        required = col1.checkbox("Required", value=True, key=f"field_required_{section_name}")
        help_text = col2.text_area("Help Text", key=f"field_help_{section_name}", height=60)
        
        if st.button("✅ Add Field", key=f"add_field_{section_name}", use_container_width=True):
            if not field_id or not label or not field_type:
                st.error("Field ID, Label, and Type are required.")
                return
            
            try:
                validation = FieldValidation(required=required)
                self.builder.add_field(
                    section_name=section_name,
                    field_id=field_id,
                    label=label,
                    field_type=FieldType(field_type),
                    placeholder=placeholder,
                    description=description,
                    help_text=help_text,
                    validation=validation,
                )
                st.success(f"✅ Field '{label}' added!")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding field: {e}")
    
    def _render_field_editor(self, section_name: str, field: FormField) -> None:
        """UI for editing an existing field"""
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 1])
            col1.caption(f"ID: {field.id}")
            col2.write(f"**{field.label}** ({field.field_type.value})")
            
            if col3.button("🗑️", key=f"remove_field_{field.id}"):
                self.builder.remove_field(section_name, field.id)
                st.success(f"Field '{field.label}' removed!")
                st.rerun()
            
            # Field details (collapsible)
            with st.expander("Edit details", expanded=False):
                field.label = st.text_input("Label", value=field.label, key=f"edit_label_{field.id}")
                field.description = st.text_area(
                    "Description", value=field.description or "", key=f"edit_desc_{field.id}"
                )
                field.validation.required = st.checkbox(
                    "Required", value=field.validation.required, key=f"edit_required_{field.id}"
                )
                field.help_text = st.text_area(
                    "Help Text", value=field.help_text or "", key=f"edit_help_{field.id}"
                )
    
    def _render_validation_view(self, form: FormDraft) -> None:
        """Display form validation results"""
        self.builder.current_form = form
        validation_result = self.builder.validate_form()
        
        if validation_result["valid"]:
            st.success("✅ Form is valid and ready to use!")
        else:
            st.error("❌ Form has validation errors:")
            for error in validation_result["errors"]:
                st.write(f"- {error}")
        
        if validation_result["warnings"]:
            st.warning("⚠️ Warnings:")
            for warning in validation_result["warnings"]:
                st.write(f"- {warning}")
        
        # Summary stats
        col1, col2, col3 = st.columns(3)
        col1.metric("Sections", validation_result["section_count"])
        col2.metric("Fields", validation_result["field_count"])
        col3.metric("Status", "Valid ✅" if validation_result["valid"] else "Invalid ❌")
    
    def _render_preview(self, form: FormDraft) -> None:
        """Show a preview of how the form will look"""
        st.info("This is how the form will appear to end users:")
        
        for section in form.sections:
            st.subheader(section.name)
            if section.description:
                st.caption(section.description)
            
            for field in section.fields:
                field_label = f"{field.label}" + (" *" if field.validation.required else "")
                
                if field.field_type == FieldType.TEXT:
                    st.text_input(
                        field_label,
                        placeholder=field.placeholder or "",
                        help=field.help_text,
                        disabled=True,
                    )
                elif field.field_type == FieldType.TEXTAREA:
                    st.text_area(
                        field_label,
                        placeholder=field.placeholder or "",
                        help=field.help_text,
                        disabled=True,
                    )
                elif field.field_type == FieldType.NUMBER:
                    st.number_input(
                        field_label,
                        min_value=field.validation.min_value,
                        max_value=field.validation.max_value,
                        help=field.help_text,
                        disabled=True,
                    )
                elif field.field_type == FieldType.SELECT:
                    options = [o["label"] for o in (field.options or [])]
                    st.selectbox(
                        field_label,
                        options=options,
                        help=field.help_text,
                        disabled=True,
                    )
                elif field.field_type == FieldType.CHECKBOX:
                    st.checkbox(field_label, help=field.help_text, disabled=True)
    
    def _render_export(self, form: FormDraft) -> None:
        """Export form configuration"""
        st.write("Export this form configuration for use in workflows.")
        
        export_format = st.radio(
            "Export format",
            ["JSON Schema", "Workflow Fields", "Python Code"],
        )
        
        self.builder.current_form = form
        
        if export_format == "JSON Schema":
            schema = self.builder.get_json_schema()
            st.json(schema)
            st.download_button(
                "📥 Download JSON Schema",
                data=st.json.dumps(schema, indent=2),
                file_name=f"{form.id}_schema.json",
                mime="application/json",
            )
        
        elif export_format == "Workflow Fields":
            fields = self.builder.to_workflow_fields()
            fields_json = [f.model_dump() for f in fields]
            st.json(fields_json)
            st.download_button(
                "📥 Download Workflow Fields",
                data=st.json.dumps(fields_json, indent=2),
                file_name=f"{form.id}_fields.json",
                mime="application/json",
            )
        
        elif export_format == "Python Code":
            code = self._generate_python_code(form)
            st.code(code, language="python")
            st.download_button(
                "📥 Download Python Code",
                data=code,
                file_name=f"{form.id}_generated.py",
                mime="text/plain",
            )
    
    def _generate_python_code(self, form: FormDraft) -> str:
        """Generate Python code from form configuration"""
        code = f'''"""Auto-generated workflow form from Phase 2 Form Builder

Form: {form.name}
Generated at: {form.updated_at.isoformat()}
"""

from phase_2_workflow_configuration.schemas import WorkflowField, FieldType, FieldValidation

FORM_FIELDS = [
'''
        
        for field in self.builder.to_workflow_fields():
            code += f'''    WorkflowField(
        id="{field.id}",
        label="{field.label}",
        field_type=FieldType.{field.field_type.name},
        description="{field.description or ''}",
        validation=FieldValidation(required={field.validation.required}),
        section="{field.section}",
    ),
'''
        
        code += "]"
        return code
