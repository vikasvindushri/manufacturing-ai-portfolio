"""Phase 2 Configuration Storage and Persistence"""
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from .schemas import (
    WorkflowConfiguration,
    WorkflowTemplate,
    PromptTemplate,
    ConfigurationPackage,
    ConfigurationExport,
)

class StorageError(Exception):
    """Storage operation error"""
    pass

class ConfigurationStorage:
    """File-based storage for workflow configurations"""
    
    def __init__(self, base_path: str = "runtime/phase2_configurations"):
        self.base_path = Path(base_path)
        self.workflows_dir = self.base_path / "workflows"
        self.templates_dir = self.base_path / "templates"
        self.prompts_dir = self.base_path / "prompts"
        self.packages_dir = self.base_path / "packages"
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create storage directories if they don't exist"""
        for directory in [self.workflows_dir, self.templates_dir, self.prompts_dir, self.packages_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # WORKFLOW CONFIGURATION OPERATIONS
    # ========================================================================
    
    def save_workflow(self, config: WorkflowConfiguration) -> str:
        """Save a workflow configuration"""
        try:
            config.updated_at = datetime.utcnow()
            path = self.workflows_dir / f"{config.id}.json"
            path.write_text(config.model_dump_json(indent=2), encoding="utf-8")
            return config.id
        except Exception as e:
            raise StorageError(f"Failed to save workflow {config.id}: {e}")
    
    def load_workflow(self, workflow_id: str) -> Optional[WorkflowConfiguration]:
        """Load a workflow configuration"""
        try:
            path = self.workflows_dir / f"{workflow_id}.json"
            if not path.exists():
                return None
            data = json.loads(path.read_text(encoding="utf-8"))
            return WorkflowConfiguration(**data)
        except Exception as e:
            raise StorageError(f"Failed to load workflow {workflow_id}: {e}")
    
    def list_workflows(self, status: Optional[str] = None) -> List[WorkflowConfiguration]:
        """List all workflows, optionally filtered by status"""
        try:
            workflows = []
            for path in self.workflows_dir.glob("*.json"):
                data = json.loads(path.read_text(encoding="utf-8"))
                config = WorkflowConfiguration(**data)
                if status is None or config.status == status:
                    workflows.append(config)
            return sorted(workflows, key=lambda x: x.created_at, reverse=True)
        except Exception as e:
            raise StorageError(f"Failed to list workflows: {e}")
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow configuration"""
        try:
            path = self.workflows_dir / f"{workflow_id}.json"
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            raise StorageError(f"Failed to delete workflow {workflow_id}: {e}")
    
    # ========================================================================
    # PROMPT TEMPLATE OPERATIONS
    # ========================================================================
    
    def save_prompt_template(self, template: PromptTemplate) -> str:
        """Save a prompt template"""
        try:
            path = self.prompts_dir / f"{template.id}_{template.version}.json"
            path.write_text(template.model_dump_json(indent=2), encoding="utf-8")
            return template.id
        except Exception as e:
            raise StorageError(f"Failed to save prompt template {template.id}: {e}")
    
    def load_prompt_template(self, template_id: str, version: Optional[str] = None) -> Optional[PromptTemplate]:
        """Load a prompt template (latest version if not specified)"""
        try:
            if version:
                path = self.prompts_dir / f"{template_id}_{version}.json"
                if path.exists():
                    data = json.loads(path.read_text(encoding="utf-8"))
                    return PromptTemplate(**data)
            else:
                # Find latest version
                paths = list(self.prompts_dir.glob(f"{template_id}_*.json"))
                if paths:
                    # Sort by version (assuming semantic versioning)
                    latest = sorted(paths)[-1]
                    data = json.loads(latest.read_text(encoding="utf-8"))
                    return PromptTemplate(**data)
            return None
        except Exception as e:
            raise StorageError(f"Failed to load prompt template {template_id}: {e}")
    
    def list_prompt_templates(self, status: Optional[str] = None) -> List[PromptTemplate]:
        """List all prompt templates (latest versions only)"""
        try:
            templates = {}
            for path in self.prompts_dir.glob("*.json"):
                data = json.loads(path.read_text(encoding="utf-8"))
                template = PromptTemplate(**data)
                if status is None or template.status == status:
                    # Keep only latest version
                    if template.id not in templates or template.version > templates[template.id].version:
                        templates[template.id] = template
            return list(templates.values())
        except Exception as e:
            raise StorageError(f"Failed to list prompt templates: {e}")
    
    # ========================================================================
    # CONFIGURATION PACKAGE OPERATIONS (IMPORT/EXPORT)
    # ========================================================================
    
    def export_package(self, package: ConfigurationPackage) -> str:
        """Export a configuration package"""
        try:
            export = ConfigurationExport(
                export_id=f"export-{package.id}-{datetime.utcnow().isoformat()}",
                package=package,
            )
            path = self.packages_dir / f"{package.id}_v{package.version}.json"
            path.write_text(export.model_dump_json(indent=2), encoding="utf-8")
            return str(path)
        except Exception as e:
            raise StorageError(f"Failed to export package {package.id}: {e}")
    
    def import_package(self, package_path: str) -> ConfigurationPackage:
        """Import a configuration package"""
        try:
            path = Path(package_path)
            if not path.exists():
                raise FileNotFoundError(f"Package file not found: {package_path}")
            data = json.loads(path.read_text(encoding="utf-8"))
            export = ConfigurationExport(**data)
            return export.package
        except Exception as e:
            raise StorageError(f"Failed to import package from {package_path}: {e}")
    
    def list_packages(self) -> List[ConfigurationPackage]:
        """List all exported packages"""
        try:
            packages = []
            for path in self.packages_dir.glob("*.json"):
                data = json.loads(path.read_text(encoding="utf-8"))
                export = ConfigurationExport(**data)
                packages.append(export.package)
            return sorted(packages, key=lambda x: x.created_at, reverse=True)
        except Exception as e:
            raise StorageError(f"Failed to list packages: {e}")
    
    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================
    
    def apply_package(self, package: ConfigurationPackage) -> Dict[str, Any]:
        """Apply all configurations from a package"""
        try:
            results = {
                "workflows_imported": 0,
                "templates_imported": 0,
                "prompts_imported": 0,
                "errors": [],
            }
            
            # Import workflows
            for workflow in package.workflows:
                try:
                    self.save_workflow(workflow)
                    results["workflows_imported"] += 1
                except Exception as e:
                    results["errors"].append(f"Workflow {workflow.id}: {str(e)}")
            
            # Import templates
            for template in package.templates:
                try:
                    # Templates are not stored separately in this phase
                    results["templates_imported"] += 1
                except Exception as e:
                    results["errors"].append(f"Template {template.id}: {str(e)}")
            
            # Import prompts
            for prompt in package.prompt_templates:
                try:
                    self.save_prompt_template(prompt)
                    results["prompts_imported"] += 1
                except Exception as e:
                    results["errors"].append(f"Prompt {prompt.id}: {str(e)}")
            
            return results
        except Exception as e:
            raise StorageError(f"Failed to apply package: {e}")
    
    def backup(self, backup_path: str) -> str:
        """Create a backup of all configurations"""
        try:
            import shutil
            backup_dir = Path(backup_path) / f"backup-{datetime.utcnow().isoformat()}"
            shutil.copytree(self.base_path, backup_dir)
            return str(backup_dir)
        except Exception as e:
            raise StorageError(f"Failed to create backup: {e}")
