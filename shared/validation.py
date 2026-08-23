from datetime import datetime
def required_text(value,label,errors):
    value=(value or "").strip()
    if not value: errors.append(f"{label} is required.")
    return value
def nonnegative_int(value,label,errors):
    try: value=int(value)
    except (TypeError,ValueError): errors.append(f"{label} must be a whole number."); return 0
    if value<0: errors.append(f"{label} cannot be negative.")
    return value
def validate_quality(data):
    e=[];out=dict(data)
    for key,label in [("incident_id","Incident ID"),("plant","Plant"),("line","Line"),("part_number","Part number"),("process","Process"),("defect","Defect"),("symptoms","Symptoms"),("detection","Detection method"),("immediate_action","Immediate action"),("owner","Owner")]:out[key]=required_text(out.get(key),label,e)
    out["quantity_affected"]=nonnegative_int(out.get("quantity_affected"),"Quantity affected",e)
    if not out.get("date"):e.append("Incident date is required.")
    return out,e
def validate_fault(data):
    e=[];out=dict(data)
    for key,label in [("fault_id","Fault ID"),("asset","Asset"),("area","Area"),("description","Description"),("reported_by","Reported by")]:out[key]=required_text(out.get(key),label,e)
    return out,e
def validate_query(q):
    q=(q or "").strip();return q,([] if len(q)>=5 else ["Enter a question with at least 5 characters."])
