import argparse,json
from .retriever import chunks_from_dir,LocalRetriever
p=argparse.ArgumentParser();p.add_argument("--query",required=True);p.add_argument("--knowledge-base",default="project_2_rag/knowledge_base")
a=p.parse_args();r=LocalRetriever(chunks_from_dir(a.knowledge_base));print(json.dumps(r.answer(a.query),indent=2))
