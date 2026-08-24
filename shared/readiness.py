QUALITY_EVIDENCE = {
    "incident_id":"Incident identified","date":"Incident date recorded","plant":"Plant identified",
    "line":"Line or area identified","part_number":"Part number recorded","process":"Process identified",
    "defect":"Defect statement recorded","quantity_affected":"Affected quantity recorded",
    "symptoms":"Observed condition described","detection":"Detection method recorded",
    "immediate_action":"Immediate containment recorded","owner":"Responsible owner assigned"
}
FAULT_EVIDENCE = {"fault_id":"Fault identified","asset":"Asset identified","area":"Area identified",
                  "description":"Fault condition described","reported_by":"Reporter identified","timestamp":"Timestamp recorded"}

def readiness(data, requirements):
    completed=[];missing=[]
    for key,label in requirements.items():
        value=data.get(key)
        if value not in (None,"",[],"UNKNOWN"): completed.append(label)
        else: missing.append(label)
    total=len(requirements);score=round(100*len(completed)/total) if total else 100
    return {"score":score,"completed":completed,"missing":missing,"complete_count":len(completed),"total_count":total,
            "label":"High" if score>=90 else "Moderate" if score>=70 else "Low"}

def quality_readiness(data):return readiness(data,QUALITY_EVIDENCE)
def fault_readiness(data):return readiness(data,FAULT_EVIDENCE)
