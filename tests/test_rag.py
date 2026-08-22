from project_2_rag.retriever import chunks_from_dir,LocalRetriever
def test_retrieval_has_reference():
    r=LocalRetriever(chunks_from_dir("project_2_rag/knowledge_base")).answer("torque calibration")
    assert r["references"] and "torque_control.md" in r["references"][0]
def test_no_evidence():
    r=LocalRetriever(chunks_from_dir("project_2_rag/knowledge_base")).answer("quantum astrophysics")
    assert r["references"]==[]
