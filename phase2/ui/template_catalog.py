"""Read-only Template Catalog and safe clone preview."""
from __future__ import annotations
import json,re
import streamlit as st
from phase2.registry import available_tags,clone_as_draft,get_template,list_templates,search_templates

def _slug(value:str)->str:
 value=re.sub(r"[^a-z0-9_-]+","_",value.lower()).strip("_")
 return (value or "workflow_draft")[:64]

def render_template_catalog():
 st.markdown("### Template Catalog")
 st.caption("Browse governed Workflow Definition Contract 1.1 templates. Catalog actions create preview drafts only and do not write operational records.")
 all_items=list_templates();left,right=st.columns([2,1]);query=left.text_input("Search templates",placeholder="quality, fault, audit, knowledge...");tag=right.selectbox("Domain filter",["all"]+available_tags())
 items=search_templates(query,tag)
 st.metric("Matching templates",len(items),f"{len(all_items)} available")
 if not items:st.info("No templates match the current search and filter.");return
 labels={f"{x.name} · {x.version}":x for x in items};label=st.selectbox("Select a template",list(labels));summary=labels[label];workflow=get_template(summary.workflow_id)
 a,b,c,d=st.columns(4);a.metric("Fields",summary.field_count);b.metric("Rules",summary.rule_count);c.metric("Prompts",summary.prompt_count);d.metric("Synthetic tests",summary.test_case_count)
 st.write(summary.description);st.caption(f"Workflow ID: {summary.workflow_id} | Status: {summary.status} | Contract: {workflow.metadata.definition_version} | AI: {'optional' if summary.ai_enabled else 'local'}")
 st.write("Tags: "+", ".join(summary.tags));st.success("Definition validated successfully. Human approval is required.")
 with st.expander("Governance summary",expanded=True):
  st.write(f"- Approval roles: {', '.join(workflow.approval.allowed_roles)}")
  st.write(f"- Creator may approve: {'Yes' if workflow.approval.creator_may_approve else 'No'}")
  st.write(f"- Local fallback: {workflow.ai_policy.fallback}")
  st.write("- Committed preview cases: synthetic only")
 with st.expander("Definition preview"):
  st.json(workflow.model_dump(mode="json"))
 st.markdown("#### Clone as draft preview")
 c1,c2=st.columns(2);new_id=c1.text_input("New workflow ID",value=_slug(summary.workflow_id.replace("_v1","")+"_draft"));new_name=c2.text_input("Draft name",value=summary.name+" Draft")
 if st.button("Create preview draft",type="primary"):
  try:draft=clone_as_draft(workflow,_slug(new_id),new_name);payload=json.dumps(draft.model_dump(mode="json"),indent=2);st.session_state["phase2_preview_draft"]=payload;st.success("Preview draft created in this browser session. No repository or operational record was changed.")
  except Exception as exc:st.error(f"Draft could not be created: {exc}")
 if st.session_state.get("phase2_preview_draft"):
  st.download_button("Download preview draft JSON",st.session_state["phase2_preview_draft"],file_name="workflow-draft-preview.json",mime="application/json")
