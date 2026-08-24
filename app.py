import json, os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from shared.ui import page,governance_note,metric_row
from shared.config import load_config
from shared.validation import validate_quality,validate_fault,validate_query
from shared.audit import audit_event
from shared.history import add_history,save_draft,load_draft
from shared.gemini_service import enabled,generate_structured,generate_grounded_answer,model_name
from shared.schemas import GeminiQualityReview,GeminiTriageReview
from project_1_quality_8d.engine import build_8d
from project_2_rag.retriever import chunks_from_dir,LocalRetriever
from project_3_low_code_agent.agent import triage
from shared.documents import quality_markdown,knowledge_markdown,fault_markdown,markdown_to_html
from services.workflows import run_quality,run_knowledge,run_fault
from shared.readiness import quality_readiness,fault_readiness
from shared.presentation import source_banner,readiness_panel,analysis_sections,report_header
from shared.health import system_health
ROOT=Path(__file__).resolve().parent
APP_VERSION="0.4"
st.set_page_config(page_title="Manufacturing AI Studio",page_icon="🏭",layout="wide",initial_sidebar_state="expanded")
try: cfg=load_config()
except ValueError as exc: st.error(str(exc));st.stop()

def log(kind,product,status="success",meta=None):
    event=audit_event(kind,product,status,meta,cfg.audit_log_path,cfg.telemetry_enabled)
    st.session_state["last_audit"]=event

def errors(items):
    st.error("Please correct the following before continuing:")
    for x in items: st.write(f"- {x}")
    st.info("Your entries remain on screen. Correct the highlighted information and try again.")

def show_ai_status(record):
    source_banner(record)

def download_record(label,record,name,document_text=None,document_stem=None):
    st.download_button(label,json.dumps(record,indent=2),name,"application/json",use_container_width=True)
    if document_text and document_stem:
        c1,c2=st.columns(2)
        c1.download_button("Download readable document (.md)",document_text,f"{document_stem}.md","text/markdown",use_container_width=True)
        c2.download_button("Download printable document (.html)",markdown_to_html(document_text,document_stem.replace('_',' ').title()),f"{document_stem}.html","text/html",use_container_width=True)

def quality_form():
    page("Quality & 8D Assistant","Guided incident intake, review, approval, and export.","QUALITY")
    governance_note("Root cause, product disposition, and permanent corrective action require qualified approval.")
    data_class=st.selectbox("Data classification",["Synthetic / demonstration","Public","Internal non-sensitive","Confidential / restricted"],key="q_class")
    case_ai=st.checkbox("Request optional Gemini review for this case",value=cfg.gemini_enabled and data_class in ["Synthetic / demonstration","Public","Internal non-sensitive"],disabled=(not cfg.gemini_enabled or data_class=="Confidential / restricted"),key="q_ai")
    if data_class=="Confidential / restricted":st.info("Local processing only. Optional Gemini review is disabled for this classification.")
    samples={"Torque control":"project_1_quality_8d/data/sample_incident.json","Bearing seating":"project_1_quality_8d/data/bearing_incident.json"}
    choice=st.selectbox("Reusable scenario",list(samples)+["Blank form"],key="q_sample")
    if st.button("Load scenario",key="q_load"):
        data={} if choice=="Blank form" else json.loads((ROOT/samples[choice]).read_text())
        st.session_state["quality_draft"]=data;log("scenario_loaded","quality",meta={"scenario":choice});st.rerun()
    d=load_draft(st.session_state,"quality") or st.session_state.get("quality_draft",{})
    with st.form("quality_form"):
        a,b,c=st.columns(3)
        incident_id=a.text_input("Incident ID *",d.get("incident_id",""));date=b.date_input("Incident date *");severity=c.selectbox("Severity",["low","medium","high"],index=max(0,["low","medium","high"].index(d.get("severity","medium")) if d.get("severity") in ["low","medium","high"] else 1))
        plant=a.text_input("Plant *",d.get("plant",""));line=b.text_input("Line / area *",d.get("line",""));part=c.text_input("Part number *",d.get("part_number",""))
        process=st.text_input("Process *",d.get("process",""));defect=st.text_input("Defect statement *",d.get("defect",""));qty=st.number_input("Quantity affected *",min_value=0,value=int(d.get("quantity_affected",0) or 0))
        symptoms=st.text_area("Observed symptoms *",d.get("symptoms",""));detection=st.text_area("Detection method *",d.get("detection",""));action=st.text_area("Immediate action *",d.get("immediate_action",""));owner=st.text_input("Responsible owner *",d.get("owner",""))
        c1,c2=st.columns(2);save=c1.form_submit_button("Save draft",use_container_width=True);generate=c2.form_submit_button("Generate review",type="primary",use_container_width=True)
    payload={"incident_id":incident_id,"date":str(date),"plant":plant,"line":line,"part_number":part,"process":process,"defect":defect,"quantity_affected":qty,"symptoms":symptoms,"detection":detection,"immediate_action":action,"owner":owner,"severity":severity}
    if save: save_draft(st.session_state,"quality",payload);log("draft_saved","quality");st.success("Draft saved for this session.")
    if generate:
        clean,err=validate_quality(payload)
        if err: errors(err);log("validation_failed","quality","error",{"count":len(err)})
        else:
            try:
                requested=case_ai
                result=run_quality(clean,cfg.profile,requested,generate_structured if enabled() else None,model_name())
                st.session_state["quality_result"]=result;add_history(st.session_state,"quality",result,cfg.history_limit)
                log("record_generated","quality",meta={"incident_id":clean["incident_id"],"gemini_status":result["provenance"]["gemini_status"]})
            except Exception as exc: st.error("The review could not be generated.");st.code(str(exc));st.info("Check configuration, then retry. Local mode remains available if Gemini is disabled.");log("generation_failed","quality","error",{"error_type":type(exc).__name__})
    if "quality_result" in st.session_state:
        r=st.session_state["quality_result"]
        src=r.get("source_incident",{});ready=quality_readiness(src);r["record_readiness"]=ready;r["data_classification"]=data_class
        report_header("QUALITY INVESTIGATION REPORT",src.get("incident_id"),"Approved" if r.get("D8_closure",{}).get("approved") else "Draft — Human Review Required",src.get("owner"),r["provenance"].get("result_source","local"),APP_VERSION)
        show_ai_status(r);readiness_panel(ready,"Investigation readiness")
        facts=[f"{k.replace('_',' ').title()}: {v}" for k,v in src.items() if k not in ("missing_fields",) and v not in (None,"","UNKNOWN")]
        recs=[a.get("action","") for a in r.get("D5_actions",[]) if a.get("action")]
        analysis_sections(facts,ready["missing"],r.get("D4_root_cause_hypotheses",[]),recs)
        tabs=st.tabs(["Review and edit","AI comparison","Approval and export"])
        with tabs[0]:
            r["D2_problem"]=st.text_area("Problem statement",r["D2_problem"]);r["D3_containment"]=st.text_area("Containment actions (one per line)","\n".join(r["D3_containment"])).splitlines();st.caption("Edits are included in the exported record.")
        with tabs[1]:
            c1,c2=st.columns(2)
            with c1:st.markdown("#### Local analysis");st.write("**Root-cause hypotheses**",r["D4_root_cause_hypotheses"]);st.write("**5-Why prompts**",r["D4_five_why_prompts"])
            with c2:st.markdown("#### Optional Gemini review");st.json(r.get("gemini_review",{"status":"Not used","message":"This result was generated locally."}))
            if cfg.gemini_enabled and not r.get("provenance",{}).get("gemini_used") and data_class!="Confidential / restricted":
                if st.button("Retry optional Gemini review",key="q_retry"):
                    retry=run_quality(src,cfg.profile,True,generate_structured if enabled() else None,model_name());r["gemini_review"]=retry.get("gemini_review");r["provenance"]=retry["provenance"];log("gemini_retry","quality",meta={"gemini_status":r["provenance"]["gemini_status"]});st.rerun()
        with tabs[2]:
            decision=st.selectbox("Review decision",["Pending","Accept","Accept with modifications","Return for more information","Reject","Escalate"],key="q_decision")
            a,b=st.columns(2);approver=a.text_input("Reviewer name",key="q_approver");role=b.text_input("Reviewer role",key="q_role");rationale=st.text_area("Decision rationale",key="q_rationale");followup=st.text_area("Required follow-up",key="q_followup");evidence=st.checkbox("Evidence reviewed",key="q_evidence")
            r["human_review"]={"decision":decision,"reviewer":approver,"role":role,"rationale":rationale,"required_follow_up":followup,"evidence_reviewed":evidence}
            if decision in ("Accept","Accept with modifications") and approver and role and evidence:r["D8_closure"].update({"approved":True,"approver":approver});log("record_approved","quality",meta={"incident_id":r["source_incident"]["incident_id"],"decision":decision});st.success("Review decision captured.")
            doc=quality_markdown(r)
            st.markdown("### Clear documentation view")
            st.markdown(doc)
            download_record("Download technical data (.json)",r,"quality_case.json",doc,"quality_case_report")

def rag_app():
    page("Manufacturing Knowledge Assistant","Search local guidance, inspect evidence, and capture feedback.","KNOWLEDGE")
    governance_note("Confirm document revision, applicability, and authority before acting.")
    data_class=st.selectbox("Question data classification",["Synthetic / demonstration","Public","Internal non-sensitive","Confidential / restricted"],key="r_class")
    query_ai=st.checkbox("Request optional Gemini synthesis",value=cfg.gemini_enabled and data_class!="Confidential / restricted",disabled=(not cfg.gemini_enabled or data_class=="Confidential / restricted"),key="r_ai")
    if data_class=="Confidential / restricted":st.info("Local retrieval only. Optional Gemini synthesis is disabled for this classification.")
    @st.cache_resource
    def load():
        ch=chunks_from_dir(str(ROOT/"project_2_rag"/"knowledge_base"));return LocalRetriever(ch),ch
    retriever,chunks=load(); metric_row([("Documents",str(len(set(x['source'] for x in chunks))),None),("Evidence chunks",str(len(chunks)),None),("Mode","Gemini + retrieval" if cfg.gemini_enabled and enabled() else "Local retrieval",None)])
    examples=["What should be checked after a torque failure?","How should nonconforming product be controlled?","When should a PFMEA be reviewed?"]
    q=st.selectbox("Reusable question",examples+["Write my own question"],key="r_sample")
    custom=st.text_input("Question *",value="" if q=="Write my own question" else q,key="r_query")
    if st.button("Search approved knowledge",type="primary",use_container_width=True):
        query,err=validate_query(custom)
        if err:errors(err);log("validation_failed","knowledge","error")
        else:
            try:
                requested=query_ai
                result=run_knowledge(query,retriever,cfg.profile,requested,generate_grounded_answer if enabled() else None)
                st.session_state["rag_result"]=result;add_history(st.session_state,"knowledge",result,cfg.history_limit)
                log("search_completed","knowledge",meta={"match_count":len(result["matches"]),"gemini_status":result["provenance"]["gemini_status"]})
            except Exception as exc:st.error("Search could not be completed.");st.code(str(exc));st.info("Verify the knowledge-base files and configuration, then retry.");log("search_failed","knowledge","error",{"error_type":type(exc).__name__})
    if "rag_result" in st.session_state:
        r=st.session_state["rag_result"];r["data_classification"]=data_class
        report_header("MANUFACTURING KNOWLEDGE RECORD","Search result",r.get("status","Draft"),"Knowledge user",r.get("provenance",{}).get("result_source","local"),APP_VERSION)
        show_ai_status(r);st.subheader("Answer");st.write(r["answer"])
        for h in r["matches"]:
            with st.expander(f"{h['source']} · chunk {h['chunk']} · relevance {h['score']:.2f}"):st.write(h["text"])
        useful=st.radio("Was this result useful?",["Not rated","Yes","Partly","No"],horizontal=True,key="r_feedback")
        note=st.text_input("Feedback note",key="r_note")
        if st.button("Save feedback"):r["feedback"]={"rating":useful,"note":note};log("feedback_saved","knowledge",meta={"rating":useful});st.success("Feedback saved in this session record.")
        doc=knowledge_markdown(r)
        st.markdown("### Clear documentation view")
        st.markdown(doc)
        download_record("Download technical data (.json)",r,"knowledge_search.json",doc,"knowledge_search_report")

def fault_form():
    page("Fault Triage Agent","Guided fault intake, review, routing decision, and export.","OPERATIONS")
    governance_note("Follow approved safety and lockout/tagout requirements. Never bypass safeguards.")
    data_class=st.selectbox("Data classification",["Synthetic / demonstration","Public","Internal non-sensitive","Confidential / restricted"],key="f_class")
    case_ai=st.checkbox("Request optional Gemini review for this case",value=cfg.gemini_enabled and data_class!="Confidential / restricted",disabled=(not cfg.gemini_enabled or data_class=="Confidential / restricted"),key="f_ai")
    if data_class=="Confidential / restricted":st.info("Local processing only. Optional Gemini review is disabled for this classification.")
    samples={"Hydraulic pressure":"project_3_low_code_agent/data/sample_fault.json","Motor overheat":"project_3_low_code_agent/data/sample_overheat_fault.json"}
    choice=st.selectbox("Reusable scenario",list(samples)+["Blank form"],key="f_sample")
    if st.button("Load scenario",key="f_load"):
        data={} if choice=="Blank form" else json.loads((ROOT/samples[choice]).read_text());st.session_state["fault_draft"]=data;log("scenario_loaded","fault",meta={"scenario":choice});st.rerun()
    d=load_draft(st.session_state,"fault") or st.session_state.get("fault_draft",{})
    with st.form("fault_form"):
        a,b=st.columns(2);fid=a.text_input("Fault ID *",d.get("fault_id",""));asset=b.text_input("Asset *",d.get("asset",""));area=a.text_input("Area *",d.get("area",""));reporter=b.text_input("Reported by *",d.get("reported_by",""));shift=a.text_input("Shift",d.get("shift",""));timestamp=b.text_input("Timestamp",d.get("timestamp",""));desc=st.text_area("Fault description *",d.get("description",""),height=140)
        c1,c2=st.columns(2);save=c1.form_submit_button("Save draft",use_container_width=True);run=c2.form_submit_button("Create triage record",type="primary",use_container_width=True)
    payload={"fault_id":fid,"asset":asset,"area":area,"reported_by":reporter,"shift":shift,"timestamp":timestamp,"description":desc}
    if save:save_draft(st.session_state,"fault",payload);log("draft_saved","fault");st.success("Draft saved for this session.")
    if run:
        clean,err=validate_fault(payload)
        if err:errors(err);log("validation_failed","fault","error",{"count":len(err)})
        else:
            try:
                requested=case_ai
                r=run_fault(clean,cfg.profile,requested,generate_structured if enabled() else None,model_name())
                st.session_state["fault_result"]=r;add_history(st.session_state,"fault",r,cfg.history_limit)
                log("record_generated","fault",meta={"fault_id":clean["fault_id"],"gemini_status":r["provenance"]["gemini_status"]})
            except Exception as exc:st.error("The triage record could not be created.");st.code(str(exc));st.info("Check the form and configuration, then retry in local mode if necessary.");log("generation_failed","fault","error",{"error_type":type(exc).__name__})
    if "fault_result" in st.session_state:
        r=st.session_state["fault_result"]
        ready=fault_readiness(r.get("source",{}));r["record_readiness"]=ready;r["data_classification"]=data_class
        report_header("MANUFACTURING FAULT TRIAGE RECORD",r.get("fault_id"),r.get("status","Draft").replace("_"," ").title(),r.get("assigned_role"),r.get("provenance",{}).get("result_source","local"),APP_VERSION)
        show_ai_status(r);readiness_panel(ready,"Triage record readiness")
        facts=[f"{k.replace('_',' ').title()}: {v}" for k,v in r.get("source",{}).items() if v not in (None,"")]
        analysis_sections(facts,ready["missing"],r.get("likely_causes",[]),r.get("diagnostic_checks",[]))
        tabs=st.tabs(["Review and edit","AI comparison","Decision and export"])
        with tabs[0]:
            r["likely_causes"]=st.text_area("Likely causes (one per line)","\n".join(r["likely_causes"])).splitlines();r["diagnostic_checks"]=st.text_area("Diagnostic checks (one per line)","\n".join(r["diagnostic_checks"])).splitlines()
        with tabs[1]:
            c1,c2=st.columns(2)
            with c1:st.markdown("#### Local analysis");st.write("**Classification**",r.get("category"));st.write("**Likely causes**",r.get("likely_causes"));st.write("**Checks**",r.get("diagnostic_checks"))
            with c2:st.markdown("#### Optional Gemini review");st.json(r.get("gemini_review",{"status":"Not used","message":"This result was generated locally."}))
            if cfg.gemini_enabled and not r.get("provenance",{}).get("gemini_used") and data_class!="Confidential / restricted":
                if st.button("Retry optional Gemini review",key="f_retry"):
                    retry=run_fault(r.get("source",{}),cfg.profile,True,generate_structured if enabled() else None,model_name());r["gemini_review"]=retry.get("gemini_review");r["provenance"]=retry["provenance"];log("gemini_retry","fault",meta={"gemini_status":r["provenance"]["gemini_status"]});st.rerun()
        with tabs[2]:
            decision=st.selectbox("Reviewer decision",["Pending","Accept","Accept with modifications","Return for more information","Reject","Escalate"]);a,b=st.columns(2);reviewer=a.text_input("Reviewer name",key="f_reviewer");role=b.text_input("Reviewer role",key="f_role");note=st.text_area("Decision rationale");followup=st.text_area("Required follow-up",key="f_followup");r["review"]={"decision":decision,"reviewer":reviewer,"role":role,"note":note,"required_follow_up":followup}
            if decision!="Pending" and reviewer and role:log("review_decision","fault",meta={"decision":decision});st.success("Review decision captured.")
            doc=fault_markdown(r)
            st.markdown("### Clear documentation view")
            st.markdown(doc)
            download_record("Download technical data (.json)",r,"fault_action_record.json",doc,"fault_action_report")

def history_page():
    page("Session History","Review records created during this browser session.","HISTORY")
    history=st.session_state.get("history",[])
    if not history:st.info("No records yet. Complete a workflow to create session history.");return
    for n,item in enumerate(history,1):
        with st.expander(f"{n}. {item['product'].title()} · {item['timestamp_utc']}"):
            record=item["record"]
            if item["product"]=="quality": doc=quality_markdown(record)
            elif item["product"]=="knowledge": doc=knowledge_markdown(record)
            elif item["product"]=="fault": doc=fault_markdown(record)
            else: doc=None
            if doc: st.markdown(doc)
            download_record("Download technical data (.json)",record,f"{item['product']}_{n}.json",doc,f"{item['product']}_{n}_report" if doc else None)
    if st.button("Clear session history"):st.session_state["history"]=[];log("history_cleared","system");st.rerun()

def health_page():
    page("System Health","Current availability of core local services and optional integrations.","SYSTEM")
    st.info("Core local workflows remain available even when Gemini is disabled or unavailable.")
    for item in system_health(cfg,enabled()):
        a,b=st.columns([2,1]);a.write(item["component"]);b.success(item["status"]) if "Available" in item["status"] or "document" in item["status"] or item["status"]=="Enabled" else b.info(item["status"])
    st.markdown("### Diagnostics")
    st.code("python scripts/check_environment.py\npython scripts/test_gemini_connection.py\npython scripts/accessibility_check.py")

def about():
    page("Manufacturing AI Studio","A reliable, guided suite for quality, knowledge, and operational workflows.","HOME")
    metric_row([("Products","3","Unified"),("Profile",cfg.profile,None),("Gemini","Enabled" if cfg.gemini_enabled and enabled() else "Local mode",None),("Session records",str(len(st.session_state.get('history',[]))),None)])
    st.markdown("### Start here")
    st.write("Use the left navigation to select a workflow. Each product includes sample scenarios, validated forms, editable review, friendly recovery guidance, session history, and controlled export.")
    a,b,c=st.columns(3)
    a.info("**Quality**\n\nCreate a governed 8D investigation draft.");b.info("**Knowledge**\n\nSearch evidence and inspect references.");c.info("**Operations**\n\nCreate a reviewed fault-triage record.")
    st.markdown("### Operating controls")
    st.write("- Required fields are marked with an asterisk.\n- Gemini is optional and the local workflow remains available.\n- Every controlled result is reviewable before export.\n- Audit events avoid storing selected sensitive free-text fields.\n- Session data is cleared when the browser session ends unless the user downloads a record.")

with st.sidebar:
    st.title("Manufacturing AI Studio")
    st.caption(f"Version {APP_VERSION}")
    nav=st.radio("Navigation",["Home","Quality & 8D","Knowledge Assistant","Fault Triage","Session History","System Health"],label_visibility="collapsed")
    st.divider();st.caption(f"Profile: {cfg.profile}");st.caption(f"Gemini: {'enabled' if cfg.gemini_enabled and enabled() else 'local mode'}")
    if st.session_state.get("last_audit"):st.caption(f"Last event: {st.session_state['last_audit']['event_type']}")
{"Home":about,"Quality & 8D":quality_form,"Knowledge Assistant":rag_app,"Fault Triage":fault_form,"Session History":history_page,"System Health":health_page}[nav]()
