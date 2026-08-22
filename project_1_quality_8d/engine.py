from dataclasses import dataclass, asdict
from typing import Any

REQUIRED=("incident_id","date","plant","line","part_number","process","defect","quantity_affected","symptoms","detection","immediate_action","owner","severity")

def extract_incident(data:dict[str,Any])->dict[str,Any]:
    out={k:data.get(k,"UNKNOWN") for k in REQUIRED}
    try: out["quantity_affected"]=int(out["quantity_affected"])
    except (TypeError,ValueError): out["quantity_affected"]=0
    out["severity"]=str(out["severity"]).lower()
    out["missing_fields"]=[k for k in REQUIRED if data.get(k) in (None,"")]
    return out

def cause_candidates(i):
    text=(i.get("defect","")+" "+i.get("symptoms","")+" "+i.get("process","")).lower()
    candidates=[]
    if "torque" in text or "fasten" in text:
        candidates += ["Calibration or parameter control failure", "Tool wear or transducer drift", "Joint condition or part variation", "Operator/work-instruction deviation"]
    elif "dimension" in text:
        candidates += ["Tool wear", "Fixture location error", "Measurement-system variation", "Material variation"]
    else:
        candidates += ["Process parameter drift", "Material/input variation", "Equipment condition", "Standard-work deviation"]
    return candidates

def five_why(i):
    return [
      f"Why was '{i['defect']}' produced or observed?",
      "Why did the process control fail to prevent it?",
      "Why was the abnormal condition not detected earlier?",
      "Why did the control plan or standard work permit the gap?",
      "Why did the management system not sustain the control?"
    ]

def corrective_actions(i):
    return [
      {"type":"containment","action":i.get("immediate_action") or "Contain affected product and verify scope","verification":"Document inventory reconciliation and inspection result"},
      {"type":"corrective","action":"Validate the confirmed root cause using evidence before implementing a permanent change","verification":"Before/after capability or controlled trial"},
      {"type":"systemic","action":"Update PFMEA, control plan, work instruction and training if the confirmed cause changes risk","verification":"Document revision approval and layered audit"}
    ]

def build_8d(data):
    i=extract_incident(data)
    return {
      "status":"DRAFT_REQUIRES_HUMAN_APPROVAL",
      "D1_team":{"leader":i["owner"],"recommended_roles":["Quality","Manufacturing Engineering","Production","Maintenance"]},
      "D2_problem":f"At {i['plant']} on {i['line']}, {i['quantity_affected']} unit(s) of {i['part_number']} were associated with: {i['defect']}. Detected by {i['detection']}.",
      "D3_containment":[i["immediate_action"],"Define suspect time window and reconcile all material","Record validation evidence before release"],
      "D4_root_cause_hypotheses":cause_candidates(i),
      "D4_five_why_prompts":five_why(i),
      "D5_actions":corrective_actions(i),
      "D6_validation":["Define acceptance criteria","Run controlled verification","Confirm no adverse impact"],
      "D7_prevention":["Review similar lines/products","Update risk and control documents","Schedule effectiveness audit"],
      "D8_closure":{"approved":False,"approver":None,"evidence_required":True},
      "source_incident":i
    }
