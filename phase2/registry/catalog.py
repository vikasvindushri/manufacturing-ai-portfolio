"""Discover and summarize governed workflow templates."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from phase2.registry.loader import load_workflow

DEFAULT_TEMPLATE_DIR=Path(__file__).resolve().parents[1]/"templates"
@dataclass(frozen=True)
class TemplateSummary:
 workflow_id:str;name:str;description:str;version:str;status:str;owner:str;tags:tuple[str,...];path:Path;field_count:int;rule_count:int;prompt_count:int;test_case_count:int;ai_enabled:bool

def list_templates(directory:Path|str=DEFAULT_TEMPLATE_DIR)->list[TemplateSummary]:
 items=[]
 for path in sorted(Path(directory).glob("*.json")):
  workflow=load_workflow(path);m=workflow.metadata
  items.append(TemplateSummary(m.workflow_id,m.name,m.description,m.version,m.status.value,m.owner,tuple(m.tags),path,len(workflow.fields),len(workflow.rules),len(workflow.prompts),len(workflow.test_cases),workflow.ai_policy.enabled))
 ids=[x.workflow_id for x in items]
 if len(ids)!=len(set(ids)):raise ValueError("template workflow IDs must be unique")
 return items

def search_templates(query:str="",tag:str="all",directory:Path|str=DEFAULT_TEMPLATE_DIR)->list[TemplateSummary]:
 q=query.strip().lower();tag=tag.strip().lower()
 return [x for x in list_templates(directory) if (not q or q in x.name.lower() or q in x.description.lower() or any(q in t.lower() for t in x.tags)) and (tag=="all" or tag in {t.lower() for t in x.tags})]

def available_tags(directory:Path|str=DEFAULT_TEMPLATE_DIR)->list[str]:
 return sorted({tag for item in list_templates(directory) for tag in item.tags})

def get_template(workflow_id:str,directory:Path|str=DEFAULT_TEMPLATE_DIR):
 matches=[x for x in list_templates(directory) if x.workflow_id==workflow_id]
 if not matches:raise KeyError(f"unknown workflow template: {workflow_id}")
 return load_workflow(matches[0].path)
