import sys
from pathlib import Path
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

import json,streamlit as st
from dotenv import load_dotenv
load_dotenv()
from project_1_quality_8d.engine import build_8d
from shared.ui import page,governance_note,metric_row
from shared.gemini_service import enabled,generate_structured,GeminiUnavailable,model_name
from shared.schemas import GeminiQualityReview
st.set_page_config(page_title="Quality & 8D Assistant",page_icon="🧭",layout="wide")
page("AI Quality & 8D Assistant","Turn an incident into an evidence checklist and governed 8D draft.","QUALITY")
governance_note("Root cause, disposition and permanent corrective action require qualified engineering approval.")
with st.sidebar:
 st.header("Configuration"); st.write("AI mode", "Gemini + local" if enabled() else "Local deterministic")
 st.caption(f"Model: {model_name()}");uploaded=st.file_uploader("Upload incident JSON",type="json")
default=open("project_1_quality_8d/data/sample_incident.json").read(); raw=uploaded.getvalue().decode() if uploaded else default
left,right=st.columns([1,1.15])
with left:
 st.subheader("1 · Incident intake"); raw=st.text_area("Incident JSON",raw,height=410,label_visibility="collapsed")
 generate=st.button("Generate governed draft",type="primary",use_container_width=True)
with right:
 st.subheader("2 · Investigation workspace")
 if generate:
  try:
   incident=json.loads(raw); result=build_8d(incident); result["provenance"]={"local_engine":"rules-v2","gemini_used":False}
   if enabled():
    prompt="Review this manufacturing incident and deterministic 8D draft. Do not assert a root cause. Identify evidence gaps and hypotheses.\n"+json.dumps(result)
    result["gemini_review"]=generate_structured("You are a cautious manufacturing quality copilot. Use 8D/PFMEA reasoning and clearly separate facts from hypotheses.",prompt,GeminiQualityReview);result["provenance"].update({"gemini_used":True,"model":model_name()})
   st.session_state.result=result
  except Exception as e: st.error(f"Draft generation failed: {e}")
 if "result" in st.session_state:
  r=st.session_state.result; i=r["source_incident"]
  metric_row([("Affected",str(i["quantity_affected"]),"units"),("Severity",i["severity"],None),("Evidence gaps",str(len(i["missing_fields"])),"fields")])
  tabs=st.tabs(["8D draft","Cause analysis","Gemini review","Approval & export"])
  with tabs[0]: st.json({k:v for k,v in r.items() if k.startswith("D")})
  with tabs[1]: st.write("**Hypotheses—not confirmed causes**");st.write(r["D4_root_cause_hypotheses"]);st.write("**5-Why prompts**");st.write(r["D4_five_why_prompts"])
  with tabs[2]: st.json(r.get("gemini_review",{"status":"Enable Gemini to add a structured second-pass review."}))
  with tabs[3]:
   approver=st.text_input("Qualified approver"); evidence=st.checkbox("Evidence attached and reviewed"); approve=st.checkbox("Approve this draft for controlled follow-up")
   if approver and evidence and approve: r["D8_closure"].update({"approved":True,"approver":approver});st.success("Approval captured in export.")
   st.download_button("Download complete case record",json.dumps(r,indent=2),"quality_8d_case.json","application/json",use_container_width=True)
