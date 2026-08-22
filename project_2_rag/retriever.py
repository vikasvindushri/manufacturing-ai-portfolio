from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def chunks_from_dir(directory, words=80):
    chunks=[]
    for p in sorted(Path(directory).glob("*.md")):
        text=p.read_text(encoding="utf-8")
        tokens=text.split()
        for n,start in enumerate(range(0,len(tokens),words)):
            body=" ".join(tokens[start:start+words])
            chunks.append({"source":p.name,"chunk":n+1,"text":body})
    return chunks

class LocalRetriever:
    def __init__(self,chunks):
        if not chunks: raise ValueError("Knowledge base is empty")
        self.chunks=chunks
        self.vectorizer=TfidfVectorizer(stop_words="english",ngram_range=(1,2))
        self.matrix=self.vectorizer.fit_transform([x["text"] for x in chunks])
    def search(self,query,top_k=3,min_score=0.01):
        scores=cosine_similarity(self.vectorizer.transform([query]),self.matrix)[0]
        order=scores.argsort()[::-1]
        return [{**self.chunks[i],"score":round(float(scores[i]),4)} for i in order[:top_k] if scores[i]>=min_score]
    def answer(self,query,top_k=3):
        hits=self.search(query,top_k)
        if not hits: return {"answer":"I could not find supporting evidence in the approved local knowledge base.","references":[]}
        evidence=" ".join(h["text"] for h in hits)
        refs=[f"{h['source']}#chunk-{h['chunk']}" for h in hits]
        return {"answer":"Evidence summary: "+evidence,"references":refs,"matches":hits,"status":"EVIDENCE_BACKED_DRAFT"}
