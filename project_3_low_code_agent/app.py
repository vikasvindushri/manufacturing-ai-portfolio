import json,streamlit as st
from dotenv import load_dotenv
load_dotenv()
from project_3_low_code_agent.agent import triage
from shared.ui import page,governance_note,metric_row
from shared.gemini_service import enabled,generate_structured,model_name
from shared.schemas import GeminiTriageReview
st.set_page_config(page_title="Manufacturing Fault Triage",page_icon="🛠️",layout="wide")
page("Low-Code Manufacturing AI Agent","Classify, investigate and route faults through a reviewable action record.","OPERATIONS")
governance_note("Follow site safety and lockout/tagout requirements. Never bypass interlocks or safeguards.")
default=open("project_3_low_code_agent/data/sample_fault.json").read();a,b=st.columns([1,1.2])
with a:
 st.subheader("Fault event");raw=st.text_area("JSON payload",default,height=330,label_visibility="collapsed");run=st.button("Create triage record",type="primary",use_container_width=True)
with b:
 st.subheader("Action control center")
 if run:
  try:
   event=json.loads(raw);record=triage(event);record["provenance"]={"local_engine":"transparent-rules-v2","gemini_used":False}
   if enabled():
    record["gemini_review"]=generate_structured("You are a safety-conscious manufacturing triage copilot. Provide hypotheses and approved diagnostic categories, never instructions to bypass safeguards.",json.dumps(record),GeminiTriageReview);record["provenance"].update({"gemini_used":True,"model":model_name()})
   st.session_state.record=record
  except Exception as e:st.error(str(e))
 if "record" in st.session_state:
  r=st.session_state.record;metric_row([("Category",r['category'],None),("Priority",r['priority'],None),("Confidence",r['confidence'],None)])
  tabs=st.tabs(["Diagnostics","Gemini review","Approval","Integration payload"])
  with tabs[0]:st.write("**Likely causes**",r['likely_causes']);st.write("**Checks**",r['diagnostic_checks'])
  with tabs[1]:st.json(r.get("gemini_review",{"status":"Gemini disabled; transparent local triage remains active."}))
  with tabs[2]:
   decision=st.selectbox("Reviewer decision",["Pending","Accept","Modify","Reject"]);note=st.text_area("Review rationale");r["review"]={"decision":decision,"note":note};st.info("Only accepted or modified records should create downstream work items.")
  with tabs[3]:st.json(r);st.download_button("Download action record",json.dumps(r,indent=2),"action_record.json","application/json",use_container_width=True)
