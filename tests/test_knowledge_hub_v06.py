from knowledge_hub.service import catalog,load_chunks,search,references_for_quality,references_for_fault,stats

def test_catalog_has_at_least_50_topics():assert len(catalog())>=50
def test_every_item_has_governance_metadata():
 req={"knowledge_id","title","domain","status","revision","owner","authority","applicable_workflows","source_urls","product_family"}
 assert all(req<=set(x) and x["source_urls"] for x in catalog())
def test_shared_workflow_coverage():
 s=stats();assert all(s["workflows"][w]>=10 for w in ("quality_8d","knowledge_assistant","fault_triage"))
def test_quality_retrieves_torque_control():
 h=references_for_quality({"process":"Fastening","defect":"Torque below lower limit","symptoms":"tool trace failed"});assert any("Torque" in x["title"] or "Fasten" in x["title"] for x in h)
def test_fault_retrieves_hydraulic_guidance():
 h=references_for_fault({"asset":"Press","description":"hydraulic pressure unstable and leaking"});assert any("Hydraulic" in x["title"] for x in h)
def test_only_released_default():assert all(x["status"]=="Released" for x in load_chunks("knowledge_assistant"))
def test_safety_topic_available_to_fault():assert search("lockout hazardous energy","fault_triage")
