"""Phase 2 Configuration Manager - Workflow lifecycle and configuration management"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from phase_2_workflow_configuration.schemas import (
    WorkflowConfiguration,
    ConfigurationPackage,
    WorkflowTemplate,
    PromptTemplate,
)
from phase_2_workflow_configuration.storage import ConfigurationStorage

class ConfigurationManagerError(Exception):
    """Configuration manager error"""
    pass

class ConfigurationManager:
    """Manage workflow configurations lifecycle"""
    
    def __init__(self, storage_path: str = "runtime/phase2_configurations"):
        self.storage = ConfigurationStorage(storage_path)
    
    # ========================================================================
    # WORKFLOW CREATION FROM TEMPLATE
    # ========================================================================
    
    def create_from_template(
        self,
        template: WorkflowTemplate,
        workflow_id: str,
        workflow_name: str,
        created_by: str,
    ) -> WorkflowConfiguration:
        """Create a new workflow from a template"""
        config = WorkflowConfiguration(
            id=workflow_id,
            name=workflow_name,
            template_id=template.id,
            created_by=created_by,
            form_fields=template.form_fields.copy(),
            rules=template.rules.copy(),
            prompt_templates=template.prompt_templates.copy(),
            output_schema=template.output_schema,
        )
        return config
    
    def create_blank(
        self,
        workflow_id: str,
        workflow_name: str,
        created_by: str,
    ) -> WorkflowConfiguration:
        """Create a blank workflow from scratch"""
        config = WorkflowConfiguration(
            id=workflow_id,
            name=workflow_name,
            created_by=created_by,
        )
        return config
    
    # ========================================================================
    # WORKFLOW STATUS MANAGEMENT
    # ========================================================================
    
    def save_workflow(self, workflow: WorkflowConfiguration) -> str:
        """Save a workflow configuration"""
        return self.storage.save_workflow(workflow)
    
    def load_workflow(self, workflow_id: str) -> Optional[WorkflowConfiguration]:
        """Load a workflow configuration"""
        return self.storage.load_workflow(workflow_id)
    
    def list_workflows(
        self,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> List[WorkflowConfiguration]:
        """List workflows with optional filters"""
        workflows = self.storage.list_workflows(status)
        if created_by:
            workflows = [w for w in workflows if w.created_by == created_by]
        return workflows
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow configuration"""
        return self.storage.delete_workflow(workflow_id)
    
    def publish_workflow(self, workflow_id: str, published_by: str) -> WorkflowConfiguration:
        """Publish a workflow to active status"""
        workflow = self.load_workflow(workflow_id)
        if not workflow:
            raise ConfigurationManagerError(f"Workflow {workflow_id} not found")
        
        # Validation before publishing
        validation = self._validate_for_publication(workflow)
        if not validation["valid"]:
            raise ConfigurationManagerError(f"Cannot publish: {validation['errors']}")
        
        workflow.status = "active"
        workflow.metadata["published_by"] = published_by
        workflow.metadata["published_at"] = datetime.utcnow().isoformat()
        self.storage.save_workflow(workflow)
        return workflow
    
    def archive_workflow(self, workflow_id: str) -> WorkflowConfiguration:
        """Archive a workflow"""
        workflow = self.load_workflow(workflow_id)
        if not workflow:
            raise ConfigurationManagerError(f"Workflow {workflow_id} not found")
        
        workflow.status = "archived"
        workflow.metadata["archived_at"] = datetime.utcnow().isoformat()
        self.storage.save_workflow(workflow)
        return workflow
    
    def validate_workflow(self, workflow: WorkflowConfiguration) -> Dict[str, Any]:
        """Validate workflow configuration"""
        errors = []
        warnings = []
        
        if not workflow.name:
            errors.append("Workflow name is required")
        if not workflow.created_by:
            errors.append("Creator information is required")
        if not workflow.form_fields:
            errors.append("Workflow must have at least one form field")
        if workflow.requires_approval and not workflow.approval_roles:
            warnings.append("Approval required but no approval roles defined")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "field_count": len(workflow.form_fields),
            "rule_count": len(workflow.rules),
            "prompt_count": len(workflow.prompt_templates),
        }
    
    def _validate_for_publication(self, workflow: WorkflowConfiguration) -> Dict[str, Any]:
        """Stricter validation for publication"""
        base_validation = self.validate_workflow(workflow)
        errors = base_validation["errors"].copy()
        
        # Additional publication requirements
        if not workflow.output_schema:
            errors.append("Output schema must be defined before publication")
        if not workflow.prompt_templates:
            errors.append("At least one prompt template must be defined")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }
    
    # ========================================================================
    # CONFIGURATION PACKAGES (IMPORT/EXPORT)
    # ========================================================================
    
    def create_package(
        self,
        package_id: str,
        package_name: str,
        workflows: List[WorkflowConfiguration],
        created_by: str,
        version: str = "1.0",
        description: Optional[str] = None,
    ) -> ConfigurationPackage:
        """Create a configuration package"""
        package = ConfigurationPackage(
            id=package_id,
            name=package_name,
            description=description,
            version=version,
            created_by=created_by,
            workflows=workflows,
        )
        return package
    
    def export_package(self, package: ConfigurationPackage) -> str:
        """Export a configuration package"""
        return self.storage.export_package(package)
    
    def import_package(self, package_path: str) -> ConfigurationPackage:
        """Import a configuration package"""
        return self.storage.import_package(package_path)
    
    def apply_package(self, package: ConfigurationPackage) -> Dict[str, Any]:
        """Apply all configurations from a package"""
        return self.storage.apply_package(package)
    
    def list_packages(self) -> List[ConfigurationPackage]:
        """List all configuration packages"""
        return self.storage.list_packages()
    
    # ========================================================================
    # CLONING AND VERSIONING
    # ========================================================================
    
    def clone_workflow(
        self,
        source_workflow_id: str,
        new_workflow_id: str,
        new_workflow_name: str,
        created_by: str,
    ) -> Optional[WorkflowConfiguration]:
        """Clone an existing workflow"""
        source = self.load_workflow(source_workflow_id)
        if not source:
            return None
        
        cloned = WorkflowConfiguration(
            id=new_workflow_id,
            name=new_workflow_name,
            template_id=source.template_id,
            version="1.0",
            status="draft",
            created_by=created_by,
            form_fields=source.form_fields.copy(),
            rules=source.rules.copy(),
            prompt_templates=source.prompt_templates.copy(),
            output_schema=source.output_schema,
        )
        
        cloned.metadata["cloned_from"] = source_workflow_id
        cloned.metadata["cloned_at"] = datetime.utcnow().isoformat()
        
        return cloned
    
    def create_version(
        self,
        workflow_id: str,
        new_version: str,
        created_by: str,
    ) -> Optional[WorkflowConfiguration]:
        """Create a new version of a workflow"""
        source = self.load_workflow(workflow_id)
        if not source:
            return None
        
        versioned = WorkflowConfiguration(
            id=f"{workflow_id}-v{new_version}",
            name=source.name,
            template_id=source.template_id,
            version=new_version,
            status="draft",
            created_by=created_by,
            form_fields=source.form_fields.copy(),
            rules=source.rules.copy(),
            prompt_templates=source.prompt_templates.copy(),
            output_schema=source.output_schema,
        )
        
        versioned.metadata["based_on_version"] = source.version
        versioned.metadata["version_created_at"] = datetime.utcnow().isoformat()
        
        return versioned
    
    # ========================================================================
    # ANALYTICS AND REPORTING
    # ========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get configuration statistics"""
        workflows = self.storage.list_workflows()
        
        status_counts = {}
        for workflow in workflows:
            status_counts[workflow.status] = status_counts.get(workflow.status, 0) + 1
        
        return {
            "total_workflows": len(workflows),
            "by_status": status_counts,
            "active_count": status_counts.get("active", 0),
            "draft_count": status_counts.get("draft", 0),
            "testing_count": status_counts.get("testing", 0),
            "archived_count": status_counts.get("archived", 0),
            "total_fields": sum(len(w.form_fields) for w in workflows),
            "total_rules": sum(len(w.rules) for w in workflows),
            "total_prompts": sum(len(w.prompt_templates) for w in workflows),
        }
    
    def export_audit_log(self) -> List[Dict[str, Any]]:
        """Export audit trail of all workflows"""
        workflows = self.storage.list_workflows()
        audit_entries = []
        
        for workflow in workflows:
            audit_entries.append({
                "workflow_id": workflow.id,
                "name": workflow.name,
                "status": workflow.status,
                "created_by": workflow.created_by,
                "created_at": workflow.created_at.isoformat(),
                "updated_at": workflow.updated_at.isoformat(),
                "version": workflow.version,
                "template_id": workflow.template_id,
            })
        
        return sorted(audit_entries, key=lambda x: x["created_at"], reverse=True)
