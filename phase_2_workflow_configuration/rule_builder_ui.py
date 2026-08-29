"""Phase 2 Rule Builder UI - Streamlit components for rule configuration"""
import streamlit as st
from typing import Optional, List
from phase_2_workflow_configuration.rule_builder import RuleBuilder, RuleDraft
from phase_2_workflow_configuration.schemas import Operator, LogicOperator

class RuleBuilderUI:
    """Streamlit UI for building workflow rules"""
    
    def __init__(self):
        self.builder = RuleBuilder()
        if "rule_builder_session" not in st.session_state:
            st.session_state.rule_builder_session = {"rule": None}
    
    # ========================================================================
    # MAIN UI COMPONENTS
    # ========================================================================
    
    def render_rule_creation(self) -> Optional[RuleDraft]:
        """UI for creating a new rule"""
        st.subheader("➕ Create New Rule")
        
        col1, col2 = st.columns(2)
        workflow_id = col1.text_input("Workflow ID *", key="new_rule_workflow_id")
        rule_name = col2.text_input("Rule Name *", key="new_rule_name")
        
        rule_desc = st.text_area(
            "Rule Description",
            placeholder="What does this rule do?",
            key="new_rule_desc",
            height=80,
        )
        
        if st.button("✅ Create Rule", type="primary", use_container_width=True):
            if not workflow_id or not rule_name:
                st.error("Workflow ID and Rule Name are required.")
                return None
            
            rule = self.builder.create_rule(
                workflow_id=workflow_id,
                rule_id=f"rule-{workflow_id}-{rule_name.lower().replace(' ', '_')}",
                name=rule_name,
                created_by="current_user",  # TODO: get from session
            )
            rule.description = rule_desc
            st.session_state.rule_builder_session["rule"] = rule
            st.success(f"✅ Rule '{rule_name}' created!")
            st.rerun()
        
        return None
    
    def render_rule_editor(self, rule: RuleDraft) -> RuleDraft:
        """Main rule editing interface"""
        st.subheader(f"✏️ Editing: {rule.name}")
        
        # Rule info
        with st.expander("📝 Rule Details", expanded=False):
            rule.name = st.text_input("Rule Name", value=rule.name)
            rule.description = st.text_area("Description", value=rule.description or "")
            col1, col2 = st.columns(2)
            rule.enabled = col1.checkbox("Enabled", value=rule.enabled)
            rule.priority = col2.number_input(
                "Priority (higher = evaluated first)",
                value=rule.priority,
                min_value=0,
                max_value=1000,
            )
        
        # Tabs for different rule aspects
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["🗓 Conditions", "🎆 Actions", "📋 Test", "🔍 Validation", "💾 Export"]
        )
        
        with tab1:
            self._render_conditions_editor(rule)
        
        with tab2:
            self._render_actions_editor(rule)
        
        with tab3:
            self._render_test_interface(rule)
        
        with tab4:
            self._render_validation_view(rule)
        
        with tab5:
            self._render_export(rule)
        
        return rule
    
    def _render_conditions_editor(self, rule: RuleDraft) -> None:
        """Editor for rule conditions"""
        self.builder.current_rule = rule
        
        st.markdown("### Conditions")
        
        # Logic operator selection
        col1, col2 = st.columns([1, 3])
        col1.write("**Logic:**")
        logic = col2.radio(
            "How should conditions be combined?",
            ["AND (all must match)", "OR (any can match)"],
            horizontal=True,
            label_visibility="collapsed",
        )
        rule.logic = LogicOperator.AND if logic.startswith("AND") else LogicOperator.OR
        
        st.divider()
        
        # Add new condition
        st.markdown("#### Add Condition")
        col1, col2, col3 = st.columns(3)
        field_id = col1.text_input("Field ID *", key="new_cond_field_id")
        operator = col2.selectbox(
            "Operator *",
            options=[op.value for op in Operator],
            key="new_cond_operator",
        )
        value = col3.text_input("Value *", key="new_cond_value")
        
        if st.button("➕ Add Condition", use_container_width=True):
            if field_id and operator and value:
                try:
                    self.builder.add_condition(
                        field_id=field_id,
                        operator=Operator(operator),
                        value=value,
                    )
                    st.success(f"✅ Condition added: {field_id} {operator} {value}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding condition: {e}")
            else:
                st.error("All fields are required.")
        
        st.divider()
        
        # List existing conditions
        if rule.conditions:
            st.markdown("#### Existing Conditions")
            for idx, condition in enumerate(rule.conditions):
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
                    col1.write(f"**{condition.field_id}**")
                    col2.write(f"`{condition.operator.value}`")
                    col3.write(f"**{condition.value}**")
                    
                    if col4.button("🗑️", key=f"remove_cond_{idx}"):
                        self.builder.remove_condition(idx)
                        st.success("Condition removed!")
                        st.rerun()
        else:
            st.info("No conditions yet. Add one above to get started.")
    
    def _render_actions_editor(self, rule: RuleDraft) -> None:
        """Editor for rule actions"""
        self.builder.current_rule = rule
        
        st.markdown("### Actions (what happens when rule matches)")
        
        # Add new action
        st.markdown("#### Add Action")
        col1, col2, col3 = st.columns(3)
        
        action_type = col1.selectbox(
            "Action Type *",
            options=["route", "require_approval", "set_category", "set_severity", "set_field_value", "show_message"],
            key="new_action_type",
        )
        
        target = col2.text_input("Target (role/field/message)", key="new_action_target")
        value = col3.text_input("Value", key="new_action_value")
        
        if st.button("➕ Add Action", use_container_width=True):
            if action_type:
                try:
                    self.builder.add_action(
                        action_type=action_type,
                        target=target or None,
                        value=value or None,
                    )
                    st.success(f"✅ Action added: {action_type}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding action: {e}")
            else:
                st.error("Action type is required.")
        
        st.divider()
        
        # List existing actions
        if rule.actions:
            st.markdown("#### Existing Actions")
            for idx, action in enumerate(rule.actions):
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
                    col1.write(f"**{action.type}**")
                    col2.write(f"`{action.target or 'N/A'}`")
                    col3.write(f"**{action.value or 'N/A'}**")
                    
                    if col4.button("🗑️", key=f"remove_action_{idx}"):
                        self.builder.remove_action(idx)
                        st.success("Action removed!")
                        st.rerun()
        else:
            st.info("No actions yet. Add one above to get started.")
    
    def _render_test_interface(self, rule: RuleDraft) -> None:
        """Interface for testing the rule"""
        st.markdown("### Test Rule with Sample Data")
        
        self.builder.current_rule = rule
        
        st.markdown("Enter test data as JSON:")
        test_data_str = st.text_area(
            "Test Data (JSON)",
            value='{"field_id": "value"}',
            height=150,
            key="test_data_input",
        )
        
        if st.button("🚀 Run Test", type="primary", use_container_width=True):
            try:
                import json
                test_data = json.loads(test_data_str)
                result = self.builder.test_rule(test_data)
                
                # Display results
                col1, col2, col3 = st.columns(3)
                col1.metric("Matched", "✅ Yes" if result["matched"] else "❌ No")
                col2.metric("Conditions Evaluated", result["conditions_evaluated"])
                col3.metric("Actions Executed", result["actions_executed"])
                
                if result["matched"]:
                    st.success("Rule matched! The following actions would execute:")
                    for action in result["actions"]:
                        st.write(f"- {action['type']} → {action.get('target', 'N/A')}")
                else:
                    st.info("Rule did not match the test data.")
                
            except json.JSONDecodeError:
                st.error("Invalid JSON. Please check the test data format.")
            except Exception as e:
                st.error(f"Error running test: {e}")
    
    def _render_validation_view(self, rule: RuleDraft) -> None:
        """Display rule validation results"""
        self.builder.current_rule = rule
        validation_result = self.builder.validate_rule()
        
        if validation_result["valid"]:
            st.success("✅ Rule is valid and ready to use!")
        else:
            st.error("❌ Rule has validation errors:")
            for error in validation_result["errors"]:
                st.write(f"- {error}")
        
        if validation_result["warnings"]:
            st.warning("⚠️ Warnings:")
            for warning in validation_result["warnings"]:
                st.write(f"- {warning}")
        
        # Summary stats
        col1, col2, col3 = st.columns(3)
        col1.metric("Conditions", validation_result["condition_count"])
        col2.metric("Actions", validation_result["action_count"])
        col3.metric("Status", "Valid ✅" if validation_result["valid"] else "Invalid ❌")
    
    def _render_export(self, rule: RuleDraft) -> None:
        """Export rule configuration"""
        st.write("Export this rule configuration for use in workflows.")
        
        export_format = st.radio(
            "Export format",
            ["JSON", "Python Code"],
        )
        
        self.builder.current_rule = rule
        
        if export_format == "JSON":
            workflow_rule = self.builder.to_workflow_rule()
            rule_json = workflow_rule.model_dump()
            st.json(rule_json)
            st.download_button(
                "📥 Download JSON",
                data=st.json.dumps(rule_json, indent=2),
                file_name=f"{rule.id}.json",
                mime="application/json",
            )
        
        elif export_format == "Python Code":
            code = self._generate_python_code(rule)
            st.code(code, language="python")
            st.download_button(
                "📥 Download Python Code",
                data=code,
                file_name=f"{rule.id}_generated.py",
                mime="text/plain",
            )
    
    def _generate_python_code(self, rule: RuleDraft) -> str:
        """Generate Python code from rule configuration"""
        code = f'''"""Auto-generated workflow rule from Phase 2 Rule Builder

Rule: {rule.name}
Generated at: {rule.updated_at.isoformat()}
"""

from phase_2_workflow_configuration.schemas import WorkflowRule, Condition, RuleAction, Operator, LogicOperator

RULE = WorkflowRule(
    id="{rule.id}",
    name="{rule.name}",
    enabled={rule.enabled},
    description="{rule.description or ''}",
    conditions=[
'''
        
        for condition in rule.conditions:
            code += f'''        Condition(
            field_id="{condition.field_id}",
            operator=Operator.{condition.operator.name},
            value="{condition.value}",
        ),
'''
        
        code += f'''    ],
    logic=LogicOperator.{rule.logic.name},
    actions=[
'''
        
        for action in rule.actions:
            code += f'''        RuleAction(
            type="{action.type}",
            target="{action.target or 'None'}",
            value="{action.value or 'None'}",
        ),
'''
        
        code += "    ],\n)"
        return code
