"""Phase 2 Prompt Template Editor - Create and manage LLM prompt templates"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import re
from phase_2_workflow_configuration.schemas import PromptTemplate

class PromptEditorError(Exception):
    """Prompt editor operation error"""
    pass

class PromptDraft(BaseModel):
    """Prompt template under construction"""
    id: str
    name: str
    description: Optional[str] = None
    purpose: str  # quality_review, triage_review, knowledge_synthesis, custom
    version: str = "1.0"
    status: str = "draft"  # draft, approved, deprecated
    system_instruction: str
    user_prompt_template: str
    temperature: float = 0.2
    max_tokens: int = 2000
    model: str = "gemini-3.6-flash"
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    notes: Optional[str] = None  # For tracking changes

class PromptVariable(BaseModel):
    """Variable extracted from prompt template"""
    name: str
    description: Optional[str] = None
    required: bool = True
    type: str = "string"  # string, number, boolean, object

class PromptEditor:
    """Editor for creating and managing LLM prompt templates"""
    
    def __init__(self):
        self.current_prompt: Optional[PromptDraft] = None
    
    # ========================================================================
    # PROMPT LIFECYCLE
    # ========================================================================
    
    def create_prompt(
        self,
        prompt_id: str,
        name: str,
        purpose: str,
        system_instruction: str,
        user_prompt_template: str,
        created_by: str,
    ) -> PromptDraft:
        """Create a new prompt template draft"""
        self.current_prompt = PromptDraft(
            id=prompt_id,
            name=name,
            purpose=purpose,
            system_instruction=system_instruction,
            user_prompt_template=user_prompt_template,
            created_by=created_by,
        )
        return self.current_prompt
    
    def load_prompt(self, prompt: PromptDraft) -> PromptDraft:
        """Load an existing prompt for editing"""
        self.current_prompt = prompt
        return self.current_prompt
    
    def get_prompt(self) -> Optional[PromptDraft]:
        """Get the current prompt being edited"""
        return self.current_prompt
    
    # ========================================================================
    # PROMPT CONTENT EDITING
    # ========================================================================
    
    def set_system_instruction(self, instruction: str) -> str:
        """Set the system instruction"""
        if not self.current_prompt:
            raise PromptEditorError("No prompt loaded.")
        self.current_prompt.system_instruction = instruction
        return instruction
    
    def get_system_instruction(self) -> str:
        """Get the current system instruction"""
        if not self.current_prompt:
            return ""
        return self.current_prompt.system_instruction
    
    def set_user_prompt_template(self, template: str) -> str:
        """Set the user prompt template"""
        if not self.current_prompt:
            raise PromptEditorError("No prompt loaded.")
        self.current_prompt.user_prompt_template = template
        return template
    
    def get_user_prompt_template(self) -> str:
        """Get the current user prompt template"""
        if not self.current_prompt:
            return ""
        return self.current_prompt.user_prompt_template
    
    # ========================================================================
    # VARIABLE MANAGEMENT
    # ========================================================================
    
    def extract_variables(self) -> List[PromptVariable]:
        """Extract variables from the prompt template"""
        if not self.current_prompt:
            return []
        
        # Find all {variable_name} placeholders
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        matches = re.findall(pattern, self.current_prompt.user_prompt_template)
        
        # Remove duplicates while preserving order
        variables = []
        seen = set()
        for match in matches:
            if match not in seen:
                variables.append(PromptVariable(name=match))
                seen.add(match)
        
        return variables
    
    def validate_variables(self) -> Dict[str, Any]:
        """Validate that all variables in template are properly formatted"""
        if not self.current_prompt:
            return {"valid": False, "errors": ["No prompt loaded"]}
        
        errors = []
        warnings = []
        variables = self.extract_variables()
        
        # Check for unmatched braces
        open_braces = self.current_prompt.user_prompt_template.count('{')
        close_braces = self.current_prompt.user_prompt_template.count('}')
        if open_braces != close_braces:
            errors.append(f"Mismatched braces: {open_braces} open, {close_braces} close")
        
        # Check for invalid variable names
        invalid_pattern = r'\{([^}]*)\}'
        for match in re.finditer(invalid_pattern, self.current_prompt.user_prompt_template):
            var_name = match.group(1)
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                errors.append(f"Invalid variable name: '{var_name}'")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "variable_count": len(variables),
            "variables": [v.name for v in variables],
        }
    
    # ========================================================================
    # PARAMETER CONFIGURATION
    # ========================================================================
    
    def set_temperature(self, temperature: float) -> float:
        """Set LLM temperature (0.0-1.0)"""
        if not self.current_prompt:
            raise PromptEditorError("No prompt loaded.")
        
        if not 0.0 <= temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        
        self.current_prompt.temperature = temperature
        return temperature
    
    def set_max_tokens(self, max_tokens: int) -> int:
        """Set maximum tokens for LLM response"""
        if not self.current_prompt:
            raise PromptEditorError("No prompt loaded.")
        
        if max_tokens < 100:
            raise ValueError("Max tokens must be at least 100")
        
        self.current_prompt.max_tokens = max_tokens
        return max_tokens
    
    def set_model(self, model: str) -> str:
        """Set the LLM model"""
        if not self.current_prompt:
            raise PromptEditorError("No prompt loaded.")
        
        self.current_prompt.model = model
        return model
    
    # ========================================================================
    # TESTING AND PREVIEW
    # ========================================================================
    
    def render_prompt(self, variables: Dict[str, Any]) -> str:
        """Render the prompt template with actual variable values"""
        if not self.current_prompt:
            raise PromptEditorError("No prompt loaded.")
        
        rendered = self.current_prompt.user_prompt_template
        
        # Replace all variables
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            rendered = rendered.replace(placeholder, str(var_value))
        
        return rendered
    
    def test_render(self, test_variables: Dict[str, Any]) -> Dict[str, Any]:
        """Test rendering the prompt with sample data"""
        if not self.current_prompt:
            raise PromptEditorError("No prompt loaded.")
        
        try:
            rendered_prompt = self.render_prompt(test_variables)
            
            # Check for unreplaced variables
            unreplaced = re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', rendered_prompt)
            
            return {
                "success": len(unreplaced) == 0,
                "system_instruction": self.current_prompt.system_instruction,
                "rendered_prompt": rendered_prompt,
                "unreplaced_variables": unreplaced,
                "test_data": test_variables,
                "estimated_tokens": self._estimate_tokens(rendered_prompt),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimate of token count (4 chars ≈ 1 token)"""
        return len(text) // 4
    
    # ========================================================================
    # VERSIONING
    # ========================================================================
    
    def create_new_version(self, version: str, notes: str = "") -> PromptDraft:
        """Create a new version of the prompt"""
        if not self.current_prompt:
            raise PromptEditorError("No prompt loaded.")
        
        # Validate semantic versioning (major.minor.patch)
        if not re.match(r'^\d+\.\d+(\.\d+)?$', version):
            raise ValueError(f"Invalid version format: {version}. Use semantic versioning (e.g., 1.0 or 1.0.1)")
        
        self.current_prompt.version = version
        self.current_prompt.status = "draft"
        self.current_prompt.notes = notes
        
        return self.current_prompt
    
    def approve_prompt(self, approved_by: str) -> PromptDraft:
        """Approve a prompt template"""
        if not self.current_prompt:
            raise PromptEditorError("No prompt loaded.")
        
        validation = self.validate_prompt()
        if not validation["valid"]:
            raise PromptEditorError(f"Cannot approve: {validation['errors']}")
        
        self.current_prompt.status = "approved"
        self.current_prompt.approved_by = approved_by
        self.current_prompt.approved_at = datetime.utcnow()
        
        return self.current_prompt
    
    def deprecate_prompt(self) -> PromptDraft:
        """Mark a prompt as deprecated"""
        if not self.current_prompt:
            raise PromptEditorError("No prompt loaded.")
        
        self.current_prompt.status = "deprecated"
        return self.current_prompt
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    
    def validate_prompt(self) -> Dict[str, Any]:
        """Validate the prompt configuration"""
        if not self.current_prompt:
            return {"valid": False, "errors": ["No prompt loaded"]}
        
        errors = []
        warnings = []
        
        # Check basic properties
        if not self.current_prompt.name:
            errors.append("Prompt name is required")
        if not self.current_prompt.system_instruction:
            errors.append("System instruction is required")
        if not self.current_prompt.user_prompt_template:
            errors.append("User prompt template is required")
        
        # Check temperature
        if not 0.0 <= self.current_prompt.temperature <= 1.0:
            errors.append("Temperature must be between 0.0 and 1.0")
        
        # Check max tokens
        if self.current_prompt.max_tokens < 100:
            errors.append("Max tokens must be at least 100")
        
        # Validate variables
        var_validation = self.validate_variables()
        if not var_validation["valid"]:
            errors.extend(var_validation["errors"])
        
        # Warn about system instruction length
        if len(self.current_prompt.system_instruction) < 20:
            warnings.append("System instruction is very short")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "temperature": self.current_prompt.temperature,
            "max_tokens": self.current_prompt.max_tokens,
            "model": self.current_prompt.model,
            "version": self.current_prompt.version,
            "status": self.current_prompt.status,
        }
    
    # ========================================================================
    # CONVERSION TO SCHEMA
    # ========================================================================
    
    def to_prompt_template(self) -> PromptTemplate:
        """Convert draft to a prompt template schema"""
        if not self.current_prompt:
            raise PromptEditorError("No prompt loaded.")
        
        variables = self.extract_variables()
        
        return PromptTemplate(
            id=self.current_prompt.id,
            name=self.current_prompt.name,
            description=self.current_prompt.description,
            purpose=self.current_prompt.purpose,
            version=self.current_prompt.version,
            status=self.current_prompt.status,
            system_instruction=self.current_prompt.system_instruction,
            user_prompt_template=self.current_prompt.user_prompt_template,
            temperature=self.current_prompt.temperature,
            max_tokens=self.current_prompt.max_tokens,
            model=self.current_prompt.model,
            input_variables=[v.name for v in variables],
            created_by=self.current_prompt.created_by,
            created_at=self.current_prompt.created_at,
            approved_by=self.current_prompt.approved_by,
            approved_at=self.current_prompt.approved_at,
        )
