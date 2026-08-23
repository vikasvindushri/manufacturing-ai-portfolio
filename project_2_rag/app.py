import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from project_2_rag.retriever import chunks_from_dir,LocalRetriever
from shared.ui import page,governance_note,metric_row
from shared.gemini_service import enabled,generate_grounded_answer,model_name
st.set_page_config(page_title="Manufacturing Knowledge Assistant",page_icon="📚",layout="wide")
page("Manufacturing Knowledge Assistant","Evidence-first retrieval with optional Gemini synthesis.","RAG")
governance_note("Confirm document revision, applicability and authority before using an answer operationally.")
@st.cache_resource
def load():
 chunks=chunks_from_dir("project_2_rag/knowledge_base");return LocalRetriever(chunks),chunks
r,chunks=load();metric_row([("Documents",str(len(set(x['source'] for x in chunks))),None),("Chunks",str(len(chunks)),None),("Generator",model_name() if enabled() else "Local extractive",None)])
q=st.chat_input("Ask about torque control, nonconformance or PFMEA...")
if q:
 with st.chat_message("user"): st.write(q)
 hits=r.search(q,top_k=4)
 with st.chat_message("assistant"):
  if not hits: st.warning("No supporting evidence found in the approved local knowledge base.")
  else:
   evidence="\n\n".join(f"[{h['source']}#chunk-{h['chunk']}] {h['text']}" for h in hits)
   answer=generate_grounded_answer(q,evidence) if enabled() else "Evidence summary: "+" ".join(h["text"] for h in hits)
   st.write(answer);st.caption("Generated from retrieved evidence; verify before use.")
   for h in hits:
    with st.expander(f"{h['source']} · chunk {h['chunk']} · relevance {h['score']:.2f}"):st.write(h['text'])
