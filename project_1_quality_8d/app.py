import json, streamlit as st
from project_1_quality_8d.engine import build_8d
st.set_page_config(page_title="AI Quality & 8D Assistant",layout="wide")
st.title("AI Quality & 8D Assistant")
st.warning("Draft decision support only. Qualified personnel must validate root cause, product disposition and corrective action.")
default=open("project_1_quality_8d/data/sample_incident.json").read()
raw=st.text_area("Incident JSON",default,height=320)
if st.button("Generate draft 8D"):
    try:
        result=build_8d(json.loads(raw)); st.session_state["result"]=result
    except Exception as e: st.error(str(e))
if "result" in st.session_state:
    result=st.session_state["result"]; st.json(result)
    approver=st.text_input("Approver name")
    approved=st.checkbox("I reviewed evidence and approve this draft")
    if approved and approver:
        result["D8_closure"].update({"approved":True,"approver":approver})
        st.success("Human approval recorded in the exported record.")
    st.download_button("Download 8D JSON",json.dumps(result,indent=2),"8d_draft.json","application/json")
