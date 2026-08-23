import streamlit as st
from shared.ui import page,metric_row,governance_note
from shared.gemini_service import enabled,model_name
st.set_page_config(page_title="Manufacturing AI Portfolio",page_icon="🏭",layout="wide")
page("Advanced Manufacturing AI Portfolio","Three governed, evidence-oriented AI workflows for Quality, Knowledge and Operations.","PORTFOLIO")
metric_row([("Projects","3","Runnable"),("Automated tests","8","CI ready"),("AI modes","Local + Gemini","Configurable"),("Approval gates","3","Human owned")])
st.write("")
c1,c2,c3=st.columns(3)
for c,title,tag,body,cmd in [
(c1,"Quality & 8D Assistant","QUALITY","Structured incident intake, deterministic 8D draft, Gemini review and accountable approval.","streamlit run project_1_quality_8d/app.py"),
(c2,"Knowledge Assistant","RAG","TF-IDF evidence retrieval plus optional Gemini synthesis constrained to cited context.","streamlit run project_2_rag/app.py"),
(c3,"Fault Triage Agent","OPERATIONS","Transparent rule-based triage, optional Gemini review and low-code action record.","streamlit run project_3_low_code_agent/app.py")]:
 with c:
  st.markdown(f'<div class="card"><span class="badge">{tag}</span><h3>{title}</h3><p>{body}</p><code>{cmd}</code></div>',unsafe_allow_html=True)
st.write("")
governance_note()
st.sidebar.header("Runtime")
st.sidebar.success(f"Gemini enabled: {enabled()}") if enabled() else st.sidebar.info("Gemini disabled: local mode")
st.sidebar.caption(f"Configured model: {model_name()}")
st.sidebar.markdown("Set `ENABLE_GEMINI=true` and `GEMINI_API_KEY` in `.env` or your shell.")
