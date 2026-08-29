"""Phase 2 Prompt Template Editor UI - Streamlit components for prompt management"""
import streamlit as st
from typing import Optional, Dict, Any
import json
from phase_2_workflow_configuration.prompt_editor import PromptEditor, PromptDraft

class PromptEditorUI:
    """Streamlit UI for editing LLM prompt templates"""
    
    def __init__(self):
        self.editor = PromptEditor()
        if "prompt_editor_session" not in st.session_state:
            st.session_state.prompt_editor_session = {"prompt": None}
    
    # ========================================================================
    # MAIN UI COMPONENTS
    # ========================================================================
    
    def render_prompt_creation(self) -> Optional[PromptDraft]:
        """UI for creating a new prompt template"""
        st.subheader("➕ Create New Prompt Template")
        
        col1, col2 = st.columns(2)
        prompt_id = col1.text_input("Prompt ID *", key="new_prompt_id")
        prompt_name = col2.text_input("Prompt Name *", key="new_prompt_name")
        
        col1, col2 = st.columns(2)
        purpose = col1.selectbox(
            "Purpose *",
            options=["quality_review", "triage_review", "knowledge_synthesis", "custom"],
            key="new_prompt_purpose",
        )
        version = col2.text_input("Initial Version", value="1.0", key="new_prompt_version")
        
        description = st.text_area(
            "Description",
            placeholder="What is this prompt for?",
            key="new_prompt_desc",
            height=80,
        )
        
        system_instruction = st.text_area(
            "System Instruction *",
            placeholder="Define the AI behavior and role...",
            key="new_prompt_system",
            height=120,
        )
        
        if st.button("✅ Create Prompt", type="primary", use_container_width=True):
            if not prompt_id or not prompt_name or not system_instruction:
                st.error("Prompt ID, Name, and System Instruction are required.")
                return None
            
            prompt = self.editor.create_prompt(
                prompt_id=prompt_id,
                name=prompt_name,
                purpose=purpose,
                system_instruction=system_instruction,
                user_prompt_template="{query}",  # Default placeholder
                created_by="current_user",  # TODO: get from session
            )
            prompt.description = description
            st.session_state.prompt_editor_session["prompt"] = prompt
            st.success(f"✅ Prompt '{prompt_name}' created!")
            st.rerun()
        
        return None
    
    def render_prompt_editor(self, prompt: PromptDraft) -> PromptDraft:
        """Main prompt editing interface"""
        st.subheader(f"✏️ Editing: {prompt.name}")
        
        # Prompt metadata
        with st.expander("📝 Prompt Details", expanded=False):
            prompt.name = st.text_input("Name", value=prompt.name)
            prompt.description = st.text_area("Description", value=prompt.description or "")
            col1, col2 = st.columns(2)
            prompt.purpose = col1.selectbox(
                "Purpose",
                options=["quality_review", "triage_review", "knowledge_synthesis", "custom"],
                index=["quality_review", "triage_review", "knowledge_synthesis", "custom"].index(prompt.purpose),
            )
            prompt.status = col2.selectbox(
                "Status",
                options=["draft", "approved", "deprecated"],
                index=["draft", "approved", "deprecated"].index(prompt.status),
            )
        
        # Tabs for different aspects
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            ["📝 Content", "🖫 Variables", "⚙️ Parameters", "🧠 Test", "🔍 Validation", "💾 Export"]
        )
        
        with tab1:
            self._render_content_editor(prompt)
        
        with tab2:
            self._render_variables_view(prompt)
        
        with tab3:
            self._render_parameters_editor(prompt)
        
        with tab4:
            self._render_test_interface(prompt)
        
        with tab5:
            self._render_validation_view(prompt)
        
        with tab6:
            self._render_export(prompt)
        
        return prompt
    
    def _render_content_editor(self, prompt: PromptDraft) -> None:
        """Editor for system instruction and user prompt"""
        self.editor.current_prompt = prompt
        
        st.markdown("### System Instruction")
        st.caption("Defines the AI's behavior, role, and constraints")
        prompt.system_instruction = st.text_area(
            "System Instruction",
            value=prompt.system_instruction,
            height=150,
            label_visibility="collapsed",
            key="edit_system_instruction",
        )
        
        st.divider()
        
        st.markdown("### User Prompt Template")
        st.caption("Template with {variable} placeholders that will be replaced at runtime")
        prompt.user_prompt_template = st.text_area(
            "User Prompt Template",
            value=prompt.user_prompt_template,
            height=200,
            label_visibility="collapsed",
            key="edit_user_prompt",
        )
        
        st.info("💡 Use {variable_name} for placeholders. Variables are extracted automatically.")
    
    def _render_variables_view(self, prompt: PromptDraft) -> None:
        """Display and manage prompt variables"""
        self.editor.current_prompt = prompt
        variables = self.editor.extract_variables()
        
        st.markdown("### Prompt Variables")
        
        if variables:
            st.success(f"Found {len(variables)} variable(s):")
            for var in variables:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2])
                    col1.write(f"**{var.name}**")
                    col2.caption("Placeholder in template")
            
            # Summary
            st.markdown("### Variable Summary")
            var_text = ", ".join([f"`{v.name}`" for v in variables])
            st.write(f"Variables to provide: {var_text}")
        else:
            st.warning("No variables found in template.")
            st.info("Add {variable_name} placeholders to the template to define variables.")
        
        # Validation
        validation = self.editor.validate_variables()
        if not validation["valid"]:
            st.error("Variable validation errors:")
            for error in validation["errors"]:
                st.write(f"- {error}")
    
    def _render_parameters_editor(self, prompt: PromptDraft) -> None:
        """Editor for LLM parameters"""
        self.editor.current_prompt = prompt
        
        st.markdown("### LLM Configuration")
        
        col1, col2, col3 = st.columns(3)
        
        prompt.temperature = col1.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=prompt.temperature,
            step=0.1,
            help="Lower = more deterministic, Higher = more creative",
        )
        
        prompt.max_tokens = col2.number_input(
            "Max Tokens",
            value=prompt.max_tokens,
            min_value=100,
            max_value=10000,
            step=100,
        )
        
        prompt.model = col3.selectbox(
            "Model",
            options=["gemini-3.6-flash", "gemini-2.0-pro", "gpt-4", "claude-3"],
            index=0 if prompt.model == "gemini-3.6-flash" else 1,
        )
        
        st.divider()
        
        # Parameter presets
        st.markdown("### Quick Presets")
        col1, col2, col3 = st.columns(3)
        
        if col1.button("🚗 Deterministic", use_container_width=True):
            prompt.temperature = 0.1
            st.success("Set to deterministic (temperature: 0.1)")
            st.rerun()
        
        if col2.button("⚡ Balanced", use_container_width=True):
            prompt.temperature = 0.5
            st.success("Set to balanced (temperature: 0.5)")
            st.rerun()
        
        if col3.button("🌟 Creative", use_container_width=True):
            prompt.temperature = 0.9
            st.success("Set to creative (temperature: 0.9)")
            st.rerun()
    
    def _render_test_interface(self, prompt: PromptDraft) -> None:
        """Interface for testing the prompt"""
        self.editor.current_prompt = prompt
        variables = self.editor.extract_variables()
        
        st.markdown("### Test Prompt Rendering")
        
        if not variables:
            st.warning("No variables in template. Add {variable_name} placeholders to test.")
            return
        
        # Input fields for each variable
        st.markdown(f"Enter values for {len(variables)} variable(s):")
        test_values = {}
        
        for var in variables:
            test_values[var.name] = st.text_area(
                f"{var.name}",
                placeholder=f"Value for {var.name}...",
                height=80,
                key=f"test_var_{var.name}",
            )
        
        if st.button("🚀 Render & Test", type="primary", use_container_width=True):
            result = self.editor.test_render(test_values)
            
            if result["success"]:
                st.success("✅ Prompt rendered successfully!")
                
                # Display system instruction
                with st.expander("📝 System Instruction", expanded=False):
                    st.write(result["system_instruction"])
                
                # Display rendered prompt
                with st.expander("📄 Rendered Prompt", expanded=True):
                    st.code(result["rendered_prompt"])
                
                # Token estimate
                col1, col2 = st.columns(2)
                col1.metric("Estimated Tokens", result["estimated_tokens"])
                col2.metric("Max Tokens", prompt.max_tokens)
                
            else:
                st.error(f"Rendering failed: {result.get('error', 'Unknown error')}")
    
    def _render_validation_view(self, prompt: PromptDraft) -> None:
        """Display prompt validation results"""
        self.editor.current_prompt = prompt
        validation = self.editor.validate_prompt()
        
        if validation["valid"]:
            st.success("✅ Prompt is valid and ready to use!")
        else:
            st.error("❌ Prompt has validation errors:")
            for error in validation["errors"]:
                st.write(f"- {error}")
        
        if validation["warnings"]:
            st.warning("⚠️ Warnings:")
            for warning in validation["warnings"]:
                st.write(f"- {warning}")
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Status", validation["status"].capitalize())
        col2.metric("Version", validation["version"])
        col3.metric("Temperature", f"{validation['temperature']:.1f}")
        col4.metric("Max Tokens", validation["max_tokens"])
    
    def _render_export(self, prompt: PromptDraft) -> None:
        """Export prompt configuration"""
        st.write("Export this prompt template for use in workflows.")
        
        export_format = st.radio(
            "Export format",
            ["JSON", "Python Code", "YAML"],
        )
        
        self.editor.current_prompt = prompt
        
        if export_format == "JSON":
            template = self.editor.to_prompt_template()
            prompt_json = template.model_dump(mode='json')
            st.json(prompt_json)
            st.download_button(
                "📥 Download JSON",
                data=json.dumps(prompt_json, indent=2, default=str),
                file_name=f"{prompt.id}_v{prompt.version}.json",
                mime="application/json",
            )
        
        elif export_format == "Python Code":
            code = self._generate_python_code(prompt)
            st.code(code, language="python")
            st.download_button(
                "📥 Download Python Code",
                data=code,
                file_name=f"{prompt.id}_v{prompt.version}.py",
                mime="text/plain",
            )
        
        elif export_format == "YAML":
            template = self.editor.to_prompt_template()
            yaml_str = self._to_yaml(template.model_dump())
            st.code(yaml_str, language="yaml")
            st.download_button(
                "📥 Download YAML",
                data=yaml_str,
                file_name=f"{prompt.id}_v{prompt.version}.yaml",
                mime="text/plain",
            )
    
    def _generate_python_code(self, prompt: PromptDraft) -> str:
        """Generate Python code from prompt"""
        code = f'''"""Auto-generated prompt template from Phase 2 Prompt Editor

Prompt: {prompt.name}
Version: {prompt.version}
Generated at: {prompt.created_at.isoformat()}
"""

from phase_2_workflow_configuration.schemas import PromptTemplate

PROMPT_TEMPLATE = PromptTemplate(
    id="{prompt.id}",
    name="{prompt.name}",
    description="{prompt.description or ''}",
    purpose="{prompt.purpose}",
    version="{prompt.version}",
    status="{prompt.status}",
    system_instruction="""
{prompt.system_instruction}
    """,
    user_prompt_template="""
{prompt.user_prompt_template}
    """,
    temperature={prompt.temperature},
    max_tokens={prompt.max_tokens},
    model="{prompt.model}",
    created_by="{prompt.created_by}",
)
'''
        return code
    
    def _to_yaml(self, data: Dict[str, Any]) -> str:
        """Convert dict to YAML format"""
        lines = []
        for key, value in data.items():
            if isinstance(value, str) and '\n' in value:
                lines.append(f"{key}: |")
                for line in value.split('\n'):
                    lines.append(f"  {line}")
            elif isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
