from shared.readiness import quality_readiness,fault_readiness
from shared.health import system_health
from shared.config import load_config

def test_quality_readiness_complete():
    d={k:"x" for k in ["incident_id","date","plant","line","part_number","process","defect","quantity_affected","symptoms","detection","immediate_action","owner"]}
    assert quality_readiness(d)["score"]==100

def test_quality_readiness_missing():
    r=quality_readiness({"incident_id":"Q1"});assert r["score"]<20 and r["missing"]

def test_fault_readiness():
    r=fault_readiness({"fault_id":"F1","asset":"A","area":"L","description":"D","reported_by":"O","timestamp":"T"});assert r["score"]==100

def test_system_health_has_core_engines():
    h=system_health(load_config("local"),False);names={x["component"] for x in h};assert "Quality local engine" in names and "Fault local engine" in names
