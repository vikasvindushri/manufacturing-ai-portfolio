from project_1_quality_8d.engine import extract_incident,build_8d
def test_extract_defaults_and_int():
    x=extract_incident({"quantity_affected":"3","severity":"HIGH"})
    assert x["quantity_affected"]==3 and x["severity"]=="high"
def test_8d_requires_approval():
    r=build_8d({"incident_id":"1","defect":"torque low","quantity_affected":1})
    assert r["status"].startswith("DRAFT") and r["D8_closure"]["approved"] is False
