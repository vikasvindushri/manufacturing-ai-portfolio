from services.workflows import run_quality,run_fault,run_knowledge,LOCAL_NOTICE,FALLBACK_NOTICE
from project_2_rag.retriever import chunks_from_dir,LocalRetriever

def fail(*a,**k): raise RuntimeError("simulated outage")
def quality_data(): return {"incident_id":"Q1","date":"2026-01-01","plant":"P","line":"L","part_number":"X","process":"Fastening","defect":"Torque low","quantity_affected":1,"symptoms":"Low torque","detection":"Audit","immediate_action":"Stop","owner":"QE","severity":"high"}
def fault_data(): return {"fault_id":"F1","asset":"Press","area":"A","description":"hydraulic pressure unstable","reported_by":"Operator"}

def test_quality_local_explicit_notice():
    r=run_quality(quality_data());assert r["provenance"]["gemini_status"]=="not_requested" and "not used" in r["provenance"]["user_notice"]
def test_quality_survives_gemini_failure():
    r=run_quality(quality_data(),"gemini",True,fail,"bad-model");assert r["D2_problem"] and r["provenance"]["gemini_status"]=="failed" and r["provenance"]["result_source"]=="local"
def test_fault_survives_gemini_failure():
    r=run_fault(fault_data(),"gemini",True,fail,"bad-model");assert r["category"]=="Hydraulic system" and r["provenance"]["gemini_used"] is False
def test_knowledge_survives_gemini_failure():
    rt=LocalRetriever(chunks_from_dir("project_2_rag/knowledge_base"));r=run_knowledge("torque calibration",rt,"gemini",True,fail);assert r["matches"] and r["answer"].startswith("Evidence summary") and r["provenance"]["gemini_status"]=="failed"
def test_success_marks_gemini_used():
    gen=lambda *a,**k:{"executive_summary":"ok"};r=run_quality(quality_data(),"gemini",True,gen,"model");assert r["provenance"]["gemini_used"] is True and r["provenance"]["result_source"]=="local_plus_gemini"
