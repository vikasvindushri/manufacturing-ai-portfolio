import streamlit as st
from project_2_rag.retriever import chunks_from_dir,LocalRetriever
st.set_page_config(page_title="Manufacturing Knowledge Assistant",layout="wide")
st.title("Manufacturing Knowledge Assistant (Local RAG)")
st.caption("Retrieves evidence from local demonstration documents. Verify document revision and authority before acting.")
@st.cache_resource
def load(): return LocalRetriever(chunks_from_dir("project_2_rag/knowledge_base"))
q=st.text_input("Question","What should be checked after a torque failure?")
if st.button("Search"):
    result=load().answer(q); st.subheader("Answer"); st.write(result["answer"])
    st.subheader("References")
    for x in result.get("matches",[]):
        with st.expander(f"{x['source']} | score {x['score']}"): st.write(x["text"])
