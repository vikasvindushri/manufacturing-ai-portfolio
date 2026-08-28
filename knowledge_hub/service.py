import json
from pathlib import Path
from project_2_rag.ingestion import chunk_document
from project_2_rag.retriever import HybridRetriever
ROOT=Path(__file__).resolve().parent

def catalog():return json.loads((ROOT/"catalog.json").read_text(encoding="utf-8"))
def load_chunks(workflow=None,status="Released"):
    out=[]
    for item in catalog():
        if status and item["status"]!=status:continue
        if workflow and workflow not in item["applicable_workflows"]:continue
        text=(ROOT/"content"/item["domain"].lower().replace(" ","_")/item["source_file"]).read_text(encoding="utf-8")
        meta={"source":item["source_file"],"title":item["title"],"document_number":item["knowledge_id"],"revision":item["revision"],"plant":"All","process":item["process"],"document_type":"Knowledge Card","status":item["status"],"owner":item["owner"],"effective_date":item["effective_date"],"confidentiality":item["confidentiality"],"domain":item["domain"],"authority":item["authority"],"applicable_workflows":item["applicable_workflows"],"source_urls":item["source_urls"]}
        out.extend(chunk_document(text,meta))
    return out

def search(query,workflow,top_k=5,filters=None):return HybridRetriever(load_chunks(workflow)).search(query,top_k=top_k,filters=filters or {"status":"Released"})
def references_for_quality(incident,top_k=4):
    q=" ".join(str(incident.get(k,"")) for k in ("process","defect","symptoms","detection","immediate_action"))
    return search(q,"quality_8d",top_k)
def references_for_fault(fault,top_k=4):
    q=" ".join(str(fault.get(k,"")) for k in ("asset","area","description"))
    return search(q,"fault_triage",top_k)
def stats():
    c=catalog();return {"topics":len(c),"domains":len({x['domain'] for x in c}),"workflows":{w:sum(w in x['applicable_workflows'] for x in c) for w in ('quality_8d','knowledge_assistant','fault_triage')},"released":sum(x['status']=='Released' for x in c)}
