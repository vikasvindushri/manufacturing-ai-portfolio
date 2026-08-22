from datetime import datetime,timezone
import uuid
RULES=[
 ({"pressure","hydraulic"},"Hydraulic system",["Check fluid level and visible leakage","Review pressure trend and filter differential","Verify sensor against a calibrated reference"],["Low fluid or leakage","Restricted filter","Pressure sensor drift"]),
 ({"temperature","overheat","hot"},"Thermal condition",["Check cooling flow and fan operation","Inspect lubrication condition","Review load and duty cycle"],["Cooling restriction","Lubrication issue","Excess load"]),
 ({"vibration","noise","bearing"},"Mechanical condition",["Collect vibration reading","Inspect bearings and alignment","Check fasteners and foundation"],["Bearing wear","Misalignment","Loose mounting"]),
 ({"torque","fasten"},"Fastening process",["Verify program and limits","Check calibration status","Review trace and joint condition"],["Incorrect parameter","Tool drift","Joint variation"])
]
def triage(fault):
    text=(fault.get("description") or "").lower(); best=None;score=0
    for keys,category,checks,causes in RULES:
        s=sum(k in text for k in keys)
        if s>score: best=(category,checks,causes);score=s
    if not best: best=("General equipment fault",["Make condition safe and preserve evidence","Review alarms and recent changes","Inspect equipment using approved procedure"],["Process change","Equipment condition","Input variation"])
    category,checks,causes=best
    return {
      "record_id":str(uuid.uuid4()),"fault_id":fault.get("fault_id"),"asset":fault.get("asset"),"category":category,
      "confidence":"medium" if score else "low","likely_causes":causes,"diagnostic_checks":checks,
      "priority":"high" if any(x in text for x in ("safety","stop","leak","overheat")) else "normal",
      "status":"AWAITING_HUMAN_REVIEW","assigned_role":"Maintenance/Manufacturing Engineering",
      "created_utc":datetime.now(timezone.utc).isoformat(),"source":fault,
      "disclaimer":"Use approved safety procedures and qualified personnel. These are diagnostic hypotheses, not instructions to bypass safeguards."
    }
