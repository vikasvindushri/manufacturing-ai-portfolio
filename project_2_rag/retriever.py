import re, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .ingestion import builtin_documents

def chunks_from_dir(directory,words=180):return builtin_documents(directory)
def _terms(text):return set(re.findall(r"[a-z0-9]+",text.lower()))
class HybridRetriever:
    def __init__(self,chunks,semantic_vectors=None):
        if not chunks:raise ValueError("Knowledge base is empty")
        self.chunks=chunks
        corpus=[self._search_text(x) for x in chunks]
        self.word=TfidfVectorizer(stop_words="english",ngram_range=(1,2),sublinear_tf=True)
        self.char=TfidfVectorizer(analyzer="char_wb",ngram_range=(3,5),min_df=1,sublinear_tf=True)
        self.word_matrix=self.word.fit_transform(corpus);self.char_matrix=self.char.fit_transform(corpus)
        self.semantic_vectors=semantic_vectors
    def _search_text(self,x):
        return " ".join(str(x.get(k,"")) for k in ("title","document_number","revision","plant","process","document_type","section","text"))
    def _filtered(self,filters):
        ids=[]
        for i,x in enumerate(self.chunks):
            ok=True
            for key,value in (filters or {}).items():
                if not value or value=="All":continue
                if str(x.get(key,"All")).lower() not in {str(value).lower(),"all"}:ok=False;break
            if ok:ids.append(i)
        return ids
    def search(self,query,top_k=5,min_score=.04,filters=None,semantic_query=None):
        ids=self._filtered(filters)
        if not ids:return []
        word=cosine_similarity(self.word.transform([query]),self.word_matrix)[0]
        char=cosine_similarity(self.char.transform([query]),self.char_matrix)[0]
        semantic=np.zeros(len(self.chunks))
        if semantic_query is not None and self.semantic_vectors is not None:
            q=np.asarray(semantic_query,float);m=np.asarray(self.semantic_vectors,float)
            semantic=cosine_similarity(q.reshape(1,-1),m)[0]
        qterms=_terms(query);rows=[]
        for i in ids:
            x=self.chunks[i];exact=len(qterms&_terms(self._search_text(x)))/max(1,len(qterms))
            score=.45*word[i]+.30*char[i]+.15*exact+.10*max(0,semantic[i])
            reasons=[]
            if word[i]>.08:reasons.append("matches key manufacturing terms")
            if char[i]>.08:reasons.append("matches related wording")
            if exact>.25:reasons.append("contains several query terms")
            if semantic[i]>.55:reasons.append("semantic meaning is similar")
            if x.get("status")=="Released":reasons.append("current released source")
            if score>=min_score:rows.append({**x,"score":round(float(score),4),"word_score":round(float(word[i]),4),"char_score":round(float(char[i]),4),"semantic_score":round(float(semantic[i]),4),"why_retrieved":reasons or ["best available local match"]})
        return sorted(rows,key=lambda x:x["score"],reverse=True)[:top_k]
class LocalRetriever(HybridRetriever):
    def answer(self,query,top_k=3):
        hits=self.search(query,top_k=top_k)
        if not hits:return {"answer":"I could not find supporting evidence in the approved local knowledge base.","references":[],"matches":[],"status":"NO_EVIDENCE"}
        refs=[f"{h['source']}#chunk-{h['chunk']}" for h in hits]
        return {"answer":"Evidence summary: "+" ".join(h["text"] for h in hits),"references":refs,"matches":hits,"status":"EVIDENCE_BACKED_DRAFT"}

