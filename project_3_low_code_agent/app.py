import json,streamlit as st
from project_3_low_code_agent.agent import triage
st.set_page_config(page_title="Manufacturing Fault Triage",layout="wide")
st.title("Low-Code Manufacturing AI Agent")
st.error("Follow site safety and lockout/tagout requirements. Do not bypass safeguards.")
default=open("project_3_low_code_agent/data/sample_fault.json").read()
raw=st.text_area("Fault event JSON",default,height=260)
if st.button("Triage fault"):
    try: st.session_state["record"]=triage(json.loads(raw))
    except Exception as e: st.error(str(e))
if "record" in st.session_state:
    r=st.session_state["record"]; st.json(r)
    decision=st.selectbox("Human decision",["Pending","Accept","Modify","Reject"])
    note=st.text_area("Reviewer note")
    r["review"]={"decision":decision,"note":note}
    st.download_button("Download action record",json.dumps(r,indent=2),"action_record.json","application/json")
