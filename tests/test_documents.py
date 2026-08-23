from shared.documents import quality_markdown,knowledge_markdown,fault_markdown,markdown_to_html

def test_quality_document_is_human_readable():
    r={"source_incident":{"incident_id":"Q1","quantity_affected":2},"D2_problem":"Torque low","D3_containment":["Stop line"],"D4_root_cause_hypotheses":["Tool drift"],"D4_five_why_prompts":["Why?"],"D5_actions":[],"D6_validation":[],"D7_prevention":[],"D8_closure":{"approved":False}}
    d=quality_markdown(r);assert "Quality Investigation" in d and "Incident ID" in d and "{\"" not in d

def test_knowledge_document_has_sources():
    d=knowledge_markdown({"question":"What?","answer":"Check it","status":"DRAFT","matches":[{"source":"a.md","chunk":1,"score":0.8,"text":"Evidence"}]})
    assert "Supporting evidence" in d and "a.md" in d

def test_fault_document_has_safety_note():
    d=fault_markdown({"fault_id":"F1","likely_causes":[],"diagnostic_checks":[],"disclaimer":"Stay safe"})
    assert "Fault Triage Record" in d and "Stay safe" in d

def test_html_export():
    h=markdown_to_html("# Report");assert "<!doctype html>" in h and "# Report" in h
