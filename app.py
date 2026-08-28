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
from shared.gemini_service import enabled,generate_structured,generate_grounded_answer,model_name,embed_texts
from shared.schemas import GeminiQualityReview,GeminiTriageReview
from project_1_quality_8d.engine import build_8d
from project_2_rag.retriever import chunks_from_dir,HybridRetriever
from project_2_rag.ingestion import extract_text,chunk_document
from project_2_rag.knowledge_service import evidence_sufficiency,local_answer,format_answer
from project_3_low_code_agent.agent import triage
from shared.documents import quality_markdown,knowledge_markdown,fault_markdown,markdown_to_html
from services.workflows import run_quality,run_knowledge,run_fault
from shared.readiness import quality_readiness,fault_readiness
from shared.presentation import source_banner,readiness_panel,analysis_sections,report_header
from shared.health import system_health
ROOT=Path(__file__).resolve().parent
APP_VERSION="0.5"
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
    page("Manufacturing Knowledge Assistant","Ask conversational questions and receive evidence-backed answers from approved local knowledge.","KNOWLEDGE")
    governance_note("Confirm document revision, applicability, and authority before acting.")
    if "kb_uploaded" not in st.session_state:st.session_state.kb_uploaded=[]
    if "kb_chat" not in st.session_state:st.session_state.kb_chat=[]
    tabs=st.tabs(["Ask knowledge","Add documents","Knowledge-base status","Evaluation"])
    with tabs[1]:
        st.subheader("Add a local document")
        uploaded=st.file_uploader("PDF, DOCX, Markdown, TXT, or CSV",type=["pdf","docx","md","txt","csv"])
        a,b,c=st.columns(3);title=a.text_input("Document title");number=b.text_input("Document number");revision=c.text_input("Revision",value="A")
        a,b,c=st.columns(3);plant=a.text_input("Plant",value="All");process=b.text_input("Process",value="General");doctype=c.selectbox("Document type",["Procedure","Work Instruction","PFMEA","Control Plan","Standard","Guidance","Other"])
        a,b,c=st.columns(3);status=a.selectbox("Approval status",["Released","Draft","Obsolete"]);owner=b.text_input("Document owner");effective=c.text_input("Effective date",value="2026-08-27")
        confidentiality=st.selectbox("Confidentiality",["Public","Internal non-sensitive","Confidential / restricted"])
        if st.button("Add document to this session",type="primary",disabled=uploaded is None):
            try:
                text=extract_text(uploaded.name,uploaded.getvalue())
                meta={"source":uploaded.name,"title":title or uploaded.name,"document_number":number or uploaded.name,"revision":revision,"plant":plant,"process":process,"document_type":doctype,"status":status,"owner":owner,"effective_date":effective,"confidentiality":confidentiality}
                chunks=chunk_document(text,meta)
                st.session_state.kb_uploaded.extend(chunks);log("knowledge_document_added","knowledge",meta={"source":uploaded.name,"chunks":len(chunks)});st.success(f"Added {uploaded.name} as {len(chunks)} searchable sections.")
            except Exception as exc:st.error("The document could not be added.");st.code(str(exc))
    base=chunks_from_dir(str(ROOT/"project_2_rag"/"knowledge_base"));chunks=base+st.session_state.kb_uploaded
    with tabs[2]:
        st.metric("Documents",len({x["source"] for x in chunks}));st.metric("Searchable sections",len(chunks));st.metric("Released sections",sum(x.get("status")=="Released" for x in chunks))
        for source in sorted({x["source"] for x in chunks}):
            sample=next(x for x in chunks if x["source"]==source)
            with st.expander(f"{sample.get('document_number')} Rev {sample.get('revision')} — {sample.get('title')}"):
                st.write({k:sample.get(k) for k in ("status","plant","process","document_type","owner","effective_date","confidentiality")});st.caption(f"{sum(x['source']==source for x in chunks)} searchable section(s)")
    with tabs[3]:
        data=json.loads((ROOT/"project_2_rag"/"evaluation"/"questions.json").read_text())
        st.write("Frozen evaluation questions with expected sources.");st.dataframe(data,use_container_width=True)
        if st.button("Run local retrieval evaluation"):
            rt=HybridRetriever(chunks);correct=0;noev=0;rows=[]
            for item in data:
                hits=rt.search(item["question"],top_k=3,filters={"status":"Released"});sources={h["source"] for h in hits}
                ok=(item["expected_source"] in sources) if item["expected_source"] else not hits
                correct+=int(ok);noev+=int(not hits);rows.append({"question":item["question"],"expected":item["expected_source"] or "No evidence","retrieved":", ".join(sources) or "No evidence","pass":ok})
            st.metric("Recall@3 / no-evidence accuracy",f"{correct/len(data):.0%}");st.dataframe(rows,use_container_width=True)
    with tabs[0]:
        st.subheader("Conversation")
        with st.expander("Search scope and options",expanded=False):
            values=lambda key:sorted({str(x.get(key,"All")) for x in chunks})
            a,b,c=st.columns(3);plant=a.selectbox("Plant",["All"]+[x for x in values("plant") if x!="All"]);process=b.selectbox("Process",["All"]+[x for x in values("process") if x!="All"]);doctype=c.selectbox("Document type",["All"]+values("document_type"))
            released=st.checkbox("Search released documents only",value=True);top_k=st.slider("Evidence sections",2,8,5)
            data_class=st.selectbox("Question data classification",["Synthetic / demonstration","Public","Internal non-sensitive","Confidential / restricted"])
            use_semantic=st.checkbox("Use optional Gemini semantic search",value=False,disabled=(not cfg.gemini_enabled or data_class=="Confidential / restricted"))
            use_synthesis=st.checkbox("Use optional Gemini conversational synthesis",value=False,disabled=(not cfg.gemini_enabled or data_class=="Confidential / restricted"))
        for msg in st.session_state.kb_chat:
            with st.chat_message(msg["role"]):st.markdown(msg["content"])
        question=st.chat_input("Ask a manufacturing knowledge question")
        if question:
            st.session_state.kb_chat.append({"role":"user","content":question})
            filters={"plant":plant,"process":process,"document_type":doctype,"status":"Released" if released else "All"}
            semantic_vectors=semantic_query=None;semantic_status="not_requested"
            if use_semantic:
                try:
                    semantic_vectors=embed_texts([f"title: {x.get('title')} | text: {x['text']}" for x in chunks],task_type="RETRIEVAL_DOCUMENT")
                    semantic_query=embed_texts([f"question answering | query: {question}"],task_type="RETRIEVAL_QUERY")[0];semantic_status="success"
                except Exception:semantic_status="failed"
            retriever=HybridRetriever(chunks,semantic_vectors);hits=retriever.search(question,top_k=top_k,filters=filters,semantic_query=semantic_query)
            sufficient=evidence_sufficiency(hits);answer=local_answer(question,hits,sufficient);gemini_status="not_requested"
            if use_synthesis and hits:
                evidence="\n\n".join(f"[S{n}] {h.get('document_number')} Rev {h.get('revision')} | {h.get('section')} | {h['text']}" for n,h in enumerate(hits,1))
                history="\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.kb_chat[-6:])
                try:
                    prompt=f"Conversation:\n{history}\n\nCurrent question: {question}\n\nEvidence:\n{evidence}\n\nAnswer conversationally. Use only evidence. Cite every key claim with [S1], [S2]. Include Direct answer, Recommended checks, Evidence limitations, and Sources."
                    answer_text=generate_grounded_answer(question,prompt);gemini_status="success"
                except Exception:answer_text=format_answer(answer);gemini_status="failed"
            else:answer_text=format_answer(answer)
            notice=("Answer synthesized from retrieved local evidence with optional Gemini AI." if gemini_status=="success" else "Answer assembled from locally retrieved evidence. Gemini AI was not used." if gemini_status=="not_requested" else "Gemini synthesis was unavailable. This answer was assembled from locally retrieved evidence.")
            content=f"**Evidence status:** {sufficient['status']}  \n**Retrieval:** Local hybrid search; semantic search {semantic_status.replace('_',' ')}  \n**Analysis source:** {notice}\n\n{answer_text}"
            result={"question":question,"answer":answer_text,"matches":hits,"status":sufficient["status"],"evidence_sufficiency":sufficient,"provenance":{"result_source":"local_plus_gemini" if gemini_status=="success" else "local","gemini_used":gemini_status=="success","gemini_status":gemini_status,"semantic_status":semantic_status,"user_notice":notice},"filters":filters}
            st.session_state["rag_result"]=result;st.session_state.kb_chat.append({"role":"assistant","content":content});add_history(st.session_state,"knowledge",result,cfg.history_limit);log("knowledge_conversation_answered","knowledge",meta={"matches":len(hits),"status":sufficient["status"],"gemini_status":gemini_status});st.rerun()
        if st.session_state.kb_chat:
            a,b=st.columns(2)
            if a.button("Start a new conversation"):st.session_state.kb_chat=[];st.rerun()
            with b.popover("Rate the latest answer"):
                rating=st.radio("Was the correct evidence found?",["Yes","Partly","No"]);grounded=st.radio("Was the answer supported?",["Yes","Partly","No"],key="grounded");note=st.text_area("What was missing?")
                if st.button("Save feedback"):log("knowledge_feedback","knowledge",meta={"evidence":rating,"supported":grounded});st.success("Feedback saved.")
        if "rag_result" in st.session_state:
            r=st.session_state.rag_result
            with st.expander("Retrieved evidence and diagnostics"):
                for n,h in enumerate(r["matches"],1):
                    st.markdown(f"#### [S{n}] {h.get('document_number')} Rev {h.get('revision')} — {h.get('section')}")
                    st.write(h["text"]);st.caption("Why retrieved: "+"; ".join(h["why_retrieved"]));st.json({k:h[k] for k in ("score","word_score","char_score","semantic_score")})
            doc=knowledge_markdown(r);download_record("Download technical record (.json)",r,"knowledge_conversation.json",doc,"knowledge_conversation_report")

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
