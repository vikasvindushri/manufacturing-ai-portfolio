from project_3_low_code_agent.agent import triage
def test_hydraulic_triage():
    r=triage({"fault_id":"1","asset":"P1","description":"hydraulic pressure unstable"})
    assert r["category"]=="Hydraulic system" and r["status"]=="AWAITING_HUMAN_REVIEW"
def test_safe_fallback():
    r=triage({"description":"unknown symptom"})
    assert r["confidence"]=="low" and r["diagnostic_checks"]
