import re

def evidence_sufficiency(hits):
    if not hits:return {"status":"No applicable evidence","reason":"No source met the retrieval threshold."}
    top=hits[0]["score"];sources=len({h.get("document_number",h["source"]) for h in hits})
    if top>=.34 and len(hits)>=2:return {"status":"Sufficient evidence","reason":"Multiple relevant evidence sections were retrieved."}
    if top>=.16:return {"status":"Partially sufficient evidence","reason":"Relevant evidence was found, but coverage may be incomplete."}
    return {"status":"Insufficient evidence","reason":"Matches are weak and should not be treated as a complete answer."}

def local_answer(question,hits,sufficiency):
    if not hits:return {"direct_answer":"I could not find applicable evidence in the selected knowledge scope.","recommended_checks":[],"limitations":["Try broader filters, add an approved document, or ask a more specific question."],"citations":[]}
    sentences=[]
    q=set(re.findall(r"[a-z0-9]+",question.lower()))
    for n,h in enumerate(hits,1):
        for sentence in re.split(r"(?<=[.!?])\s+|\n+",h["text"]):
            sentence=sentence.strip(" -")
            if len(sentence)<25:continue
            overlap=len(q & set(re.findall(r"[a-z0-9]+",sentence.lower())))
            sentences.append((overlap+h["score"],sentence,n))
    chosen=[];seen=set()
    for _,sentence,n in sorted(sentences,reverse=True):
        key=sentence.lower()
        if key in seen:continue
        seen.add(key);chosen.append((sentence,n))
        if len(chosen)==4:break
    direct=" ".join(f"{s} [S{n}]" for s,n in chosen[:2]) or "Relevant evidence was found; inspect the sources below."
    checks=[f"{s} [S{n}]" for s,n in chosen[2:]]
    limits=[] if sufficiency["status"]=="Sufficient evidence" else [sufficiency["reason"]]
    citations=[{"id":f"S{n}","document":h.get("document_number",h["source"]),"title":h.get("title",h["source"]),"revision":h.get("revision","Unknown"),"section":h.get("section","Document content"),"source":h["source"]} for n,h in enumerate(hits,1)]
    return {"direct_answer":direct,"recommended_checks":checks,"limitations":limits,"citations":citations}

def format_answer(answer):
    checks="\n".join(f"{i}. {x}" for i,x in enumerate(answer.get("recommended_checks",[]),1)) or "No additional checks were extracted."
    limits="\n".join(f"- {x}" for x in answer.get("limitations",[])) or "- No additional limitation identified."
    citations="\n".join(f"- [{x['id']}] {x['document']} Rev {x['revision']} — {x['section']}" for x in answer.get("citations",[])) or "- No supporting source."
    return f"""### Direct answer\n\n{answer.get('direct_answer','')}\n\n### Recommended checks\n\n{checks}\n\n### Evidence limitations\n\n{limits}\n\n### Sources\n\n{citations}"""
