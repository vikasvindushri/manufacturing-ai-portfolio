"""Phase 2 Tests - Unit tests for form, rule, and prompt builders"""
import pytest
from datetime import datetime
from phase_2_workflow_configuration.form_builder import FormBuilder
from phase_2_workflow_configuration.rule_builder import RuleBuilder
from phase_2_workflow_configuration.prompt_editor import PromptEditor
from phase_2_workflow_configuration.schemas import FieldType, Operator, LogicOperator

# ============================================================================
# FORM BUILDER TESTS
# ============================================================================

class TestFormBuilder:
    """Tests for FormBuilder"""
    
    def test_create_form(self):
        """Test form creation"""
        builder = FormBuilder()
        form = builder.create_form(
            workflow_id="wf-001",
            form_id="form-001",
            name="Test Form",
            created_by="test_user",
        )
        
        assert form.id == "form-001"
        assert form.name == "Test Form"
        assert form.workflow_id == "wf-001"
    
    def test_add_section(self):
        """Test section addition"""
        builder = FormBuilder()
        form = builder.create_form("wf-001", "form-001", "Test", "user")
        builder.load_form(form)
        
        section = builder.add_section("Details", "General information")
        
        assert section.name == "Details"
        assert len(builder.current_form.sections) == 1
    
    def test_add_field(self):
        """Test field addition to section"""
        builder = FormBuilder()
        form = builder.create_form("wf-001", "form-001", "Test", "user")
        builder.load_form(form)
        builder.add_section("Details")
        
        field = builder.add_field(
            section_name="Details",
            field_id="field-001",
            label="Name",
            field_type=FieldType.TEXT,
        )
        
        assert field.id == "field-001"
        assert field.label == "Name"
        assert len(builder.current_form.sections[0].fields) == 1
    
    def test_validate_form(self):
        """Test form validation"""
        builder = FormBuilder()
        form = builder.create_form("wf-001", "form-001", "Test", "user")
        builder.load_form(form)
        
        validation = builder.validate_form()
        assert not validation["valid"]  # No sections
        
        builder.add_section("Details")
        builder.add_field(
            "Details", "field-001", "Name", FieldType.TEXT
        )
        
        validation = builder.validate_form()
        assert validation["valid"]
    
    def test_remove_field(self):
        """Test field removal"""
        builder = FormBuilder()
        form = builder.create_form("wf-001", "form-001", "Test", "user")
        builder.load_form(form)
        builder.add_section("Details")
        builder.add_field("Details", "field-001", "Name", FieldType.TEXT)
        
        removed = builder.remove_field("Details", "field-001")
        assert removed
        assert len(builder.current_form.sections[0].fields) == 0

# ============================================================================
# RULE BUILDER TESTS
# ============================================================================

class TestRuleBuilder:
    """Tests for RuleBuilder"""
    
    def test_create_rule(self):
        """Test rule creation"""
        builder = RuleBuilder()
        rule = builder.create_rule(
            workflow_id="wf-001",
            rule_id="rule-001",
            name="Severity High Route",
            created_by="test_user",
        )
        
        assert rule.id == "rule-001"
        assert rule.name == "Severity High Route"
    
    def test_add_condition(self):
        """Test condition addition"""
        builder = RuleBuilder()
        rule = builder.create_rule("wf-001", "rule-001", "Test", "user")
        builder.load_rule(rule)
        
        condition = builder.add_condition(
            field_id="severity",
            operator=Operator.EQUALS,
            value="high",
        )
        
        assert condition.field_id == "severity"
        assert len(builder.current_rule.conditions) == 1
    
    def test_add_action(self):
        """Test action addition"""
        builder = RuleBuilder()
        rule = builder.create_rule("wf-001", "rule-001", "Test", "user")
        builder.load_rule(rule)
        builder.add_condition("severity", Operator.EQUALS, "high")
        
        action = builder.add_action(
            action_type="route",
            target="quality_team",
        )
        
        assert action.type == "route"
        assert len(builder.current_rule.actions) == 1
    
    def test_evaluate_rule(self):
        """Test rule evaluation"""
        builder = RuleBuilder()
        rule = builder.create_rule("wf-001", "rule-001", "Test", "user")
        builder.load_rule(rule)
        builder.add_condition("severity", Operator.EQUALS, "high")
        builder.add_action("route", target="quality_team")
        
        # Test matching data
        matched = builder.evaluate({"severity": "high"})
        assert matched
        
        # Test non-matching data
        not_matched = builder.evaluate({"severity": "low"})
        assert not not_matched
    
    def test_test_rule(self):
        """Test rule testing"""
        builder = RuleBuilder()
        rule = builder.create_rule("wf-001", "rule-001", "Test", "user")
        builder.load_rule(rule)
        builder.add_condition("severity", Operator.EQUALS, "high")
        builder.add_action("route", target="quality_team")
        
        result = builder.test_rule({"severity": "high"})
        
        assert result["matched"]
        assert result["actions_executed"] == 1

# ============================================================================
# PROMPT EDITOR TESTS
# ============================================================================

class TestPromptEditor:
    """Tests for PromptEditor"""
    
    def test_create_prompt(self):
        """Test prompt creation"""
        editor = PromptEditor()
        prompt = editor.create_prompt(
            prompt_id="prompt-001",
            name="Quality Review",
            purpose="quality_review",
            system_instruction="You are a quality expert.",
            user_prompt_template="Analyze the incident: {incident}",
            created_by="test_user",
        )
        
        assert prompt.id == "prompt-001"
        assert prompt.name == "Quality Review"
    
    def test_extract_variables(self):
        """Test variable extraction"""
        editor = PromptEditor()
        prompt = editor.create_prompt(
            "prompt-001",
            "Test",
            "custom",
            "System",
            "Analyze {incident} and {data}. Field: {field}",
            "user",
        )
        editor.load_prompt(prompt)
        
        variables = editor.extract_variables()
        
        assert len(variables) == 3
        var_names = [v.name for v in variables]
        assert "incident" in var_names
        assert "data" in var_names
        assert "field" in var_names
    
    def test_render_prompt(self):
        """Test prompt rendering"""
        editor = PromptEditor()
        prompt = editor.create_prompt(
            "prompt-001",
            "Test",
            "custom",
            "System",
            "Analyze incident: {incident}. Data: {data}",
            "user",
        )
        editor.load_prompt(prompt)
        
        rendered = editor.render_prompt({
            "incident": "Torque control failure",
            "data": "Expected 50 Nm, got 45 Nm",
        })
        
        assert "Torque control failure" in rendered
        assert "45 Nm" in rendered
    
    def test_validate_prompt(self):
        """Test prompt validation"""
        editor = PromptEditor()
        prompt = editor.create_prompt(
            "prompt-001",
            "Test",
            "custom",
            "System instruction for AI role",
            "Template with {variable}",
            "user",
        )
        editor.load_prompt(prompt)
        
        validation = editor.validate_prompt()
        
        assert validation["valid"]
        assert validation["variable_count"] == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
