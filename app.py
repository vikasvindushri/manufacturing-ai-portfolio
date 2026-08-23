import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from shared.ui import page,metric_row,governance_note
from shared.gemini_service import enabled,model_name
st.set_page_config(page_title="Manufacturing AI Studio",page_icon="🏭",layout="wide",initial_sidebar_state="expanded")
page("Manufacturing AI Studio","A governed product suite for quality investigations, evidence-backed knowledge, and operational fault triage.","PORTFOLIO")
metric_row([("Products","3","End-to-end"),("Operating modes","2","Local + Gemini"),("Approval gates","3","Human-owned"),("Current runtime","Gemini" if enabled() else "Local","Resilient")])
st.markdown("### Choose a workflow")
cols=st.columns(3)
items=[
("🧭","Quality & 8D Assistant","Create a consistent investigation draft and evidence checklist.","Quality / Engineering","python -m streamlit run project_1_quality_8d/app.py"),
("📚","Knowledge Assistant","Search approved local guidance and inspect every source.","All manufacturing users","python -m streamlit run project_2_rag/app.py"),
("🛠️","Fault Triage Agent","Standardize fault classification, review, routing and export.","Operations / Maintenance","python -m streamlit run project_3_low_code_agent/app.py")]
for c,(icon,title,body,user,cmd) in zip(cols,items):
 with c:
  st.markdown(f'<div class="card"><div style="font-size:2rem">{icon}</div><h3>{title}</h3><p>{body}</p><p><b>Primary user:</b> {user}</p><code>{cmd}</code></div>',unsafe_allow_html=True)
st.markdown("### Guided demonstration")
a,b=st.columns([1.2,1])
with a:
 st.markdown("""1. Start with the **Quality Assistant** and generate the supplied torque case.  
2. Use the **Knowledge Assistant** to ask what should be checked after a torque failure.  
3. Use the **Fault Triage Agent** to process the hydraulic-pressure example.  
4. In every product, point out evidence, provenance, fallback behavior and human approval.""")
with b:
 st.info("Product demonstration tip: lead with the manufacturing problem and measurable outcome—not the model name.")
governance_note()
with st.sidebar:
 st.header("System status")
 st.success("Gemini connected by configuration") if enabled() else st.info("Local-first mode")
 st.write("Model",model_name());st.caption("Use scripts/check_environment.py for diagnostics.")
 st.divider();st.header("Portfolio navigation")
 st.markdown("- [User guide](./docs/USER_GUIDE.md)\n- [Product demonstration playbook](./docs/PRODUCT_DEMONSTRATION.md)\n- [Product requirements](./docs/PRODUCT_REQUIREMENTS.md)")
