from html import escape

def _text(value, fallback="Not provided"):
    if value is None or value == "": return fallback
    if isinstance(value,bool): return "Yes" if value else "No"
    return str(value)

def _lines(items):
    if not items:return "- None recorded"
    return "\n".join(f"- {_text(x)}" for x in items)

def quality_markdown(r):
    src=r.get("source_incident",{}); close=r.get("D8_closure",{}); team=r.get("D1_team",{})
    actions=r.get("D5_actions",[])
    action_lines=[]
    for n,a in enumerate(actions,1):
        action_lines.append(f"{n}. **{_text(a.get('type','Action')).title()}** — {_text(a.get('action'))}\n   - Verification: {_text(a.get('verification'))}")
    review=r.get("gemini_review") or {}
    return f'''# Quality Investigation and 8D Review

## Case summary

- **Incident ID:** {_text(src.get('incident_id'))}
- **Date:** {_text(src.get('date'))}
- **Plant:** {_text(src.get('plant'))}
- **Line / area:** {_text(src.get('line'))}
- **Part number:** {_text(src.get('part_number'))}
- **Process:** {_text(src.get('process'))}
- **Severity:** {_text(src.get('severity')).title()}
- **Quantity affected:** {_text(src.get('quantity_affected'))}
- **Responsible owner:** {_text(src.get('owner'))}

## D1 — Team

- **Team leader:** {_text(team.get('leader'))}
- **Recommended roles:** {_text(', '.join(team.get('recommended_roles',[])))}

## D2 — Problem description

{_text(r.get('D2_problem'))}

## D3 — Immediate containment

{_lines(r.get('D3_containment',[]))}

## D4 — Root-cause hypotheses

> These are investigation hypotheses, not confirmed causes.

{_lines(r.get('D4_root_cause_hypotheses',[]))}

### Five-Why investigation prompts

{_lines(r.get('D4_five_why_prompts',[]))}

## D5 — Corrective-action candidates

{chr(10).join(action_lines) if action_lines else '- None recorded'}

## D6 — Validation plan

{_lines(r.get('D6_validation',[]))}

## D7 — Prevention and systemic action

{_lines(r.get('D7_prevention',[]))}

## D8 — Review and closure

- **Approved:** {_text(close.get('approved',False))}
- **Approver:** {_text(close.get('approver'))}
- **Evidence required:** {_text(close.get('evidence_required',True))}

## Result source and AI status

{_text(r.get('provenance',{}).get('user_notice'), LOCAL_NOTICE if False else "Result generated locally. Gemini AI was not used.")}

- **Gemini used:** {_text(r.get('provenance',{}).get('gemini_used',False))}
- **Executive summary:** {_text(review.get('executive_summary'),'No additional AI review was used.')}

### Missing evidence
{_lines(review.get('missing_evidence',[]))}

### Risks and cautions
{_lines(review.get('risks_and_cautions',[]))}

---

**Important:** This document is decision support. Qualified personnel must validate containment, root cause, product disposition, corrective action, and closure.
'''

def knowledge_markdown(r):
    refs=[]
    for n,h in enumerate(r.get("matches",[]),1):
        refs.append(f"### Source {n}: {_text(h.get('source'))}\n\n- **Section:** Chunk {_text(h.get('chunk'))}\n- **Relevance:** {_text(h.get('score'))}\n\n{_text(h.get('text'))}")
    feedback=r.get("feedback",{})
    return f'''# Manufacturing Knowledge Search Record

## Question

{_text(r.get('question'))}

## Answer

{_text(r.get('answer'))}

## Result status

{_text(r.get('status'))}

## Result source and AI status

{_text(r.get('provenance',{}).get('user_notice'),"Result generated locally. Gemini AI was not used.")}

## Supporting evidence

{chr(10).join(refs) if refs else 'No supporting evidence was found in the current knowledge base.'}

## User feedback

- **Rating:** {_text(feedback.get('rating'),'Not rated')}
- **Comment:** {_text(feedback.get('note'))}

---

**Important:** Confirm document revision, applicability, and authority before using this information operationally.
'''

def fault_markdown(r):
    src=r.get("source",{});review=r.get("review",{});ai=r.get("gemini_review") or {}
    return f'''# Manufacturing Fault Triage Record

## Fault summary

- **Fault ID:** {_text(r.get('fault_id'))}
- **Asset:** {_text(r.get('asset'))}
- **Area:** {_text(src.get('area'))}
- **Reported by:** {_text(src.get('reported_by'))}
- **Shift:** {_text(src.get('shift'))}
- **Reported time:** {_text(src.get('timestamp'))}
- **Description:** {_text(src.get('description'))}

## Triage assessment

- **Classification:** {_text(r.get('category'))}
- **Priority:** {_text(r.get('priority')).title()}
- **Confidence:** {_text(r.get('confidence')).title()}
- **Assigned role:** {_text(r.get('assigned_role'))}
- **Status:** {_text(r.get('status')).replace('_',' ').title()}

## Likely causes

> These are diagnostic hypotheses and must be verified.

{_lines(r.get('likely_causes',[]))}

## Recommended diagnostic checks

{_lines(r.get('diagnostic_checks',[]))}

## Result source and AI status

{_text(r.get('provenance',{}).get('user_notice'),"Result generated locally. Gemini AI was not used.")}

## AI-assisted review

- **Classification:** {_text(ai.get('classification'),'No additional AI review was used.')}
- **Rationale:** {_text(ai.get('rationale'),'Not applicable')}

### Escalation triggers
{_lines(ai.get('escalation_triggers',[]))}

## Human review

- **Decision:** {_text(review.get('decision'),'Pending')}
- **Rationale:** {_text(review.get('note'))}

## Safety note

{_text(r.get('disclaimer'))}

---

**Important:** Follow approved safety procedures and lockout/tagout requirements. Never bypass safeguards or interlocks.
'''

def markdown_to_html(md,title="Manufacturing AI Studio Record"):
    # Lightweight, dependency-free HTML export. Preserve human-readable Markdown layout in a styled <pre>.
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><style>body{{font-family:Arial,sans-serif;color:#172b3a;background:#f5f7fa;margin:0}}main{{max-width:900px;margin:32px auto;background:#fff;padding:44px;border-top:8px solid #087f8c;box-shadow:0 8px 30px #20304018}}pre{{white-space:pre-wrap;font:15px/1.6 Arial,sans-serif}}@page{{margin:18mm}}@media print{{body{{background:#fff}}main{{box-shadow:none;margin:0;max-width:none;border-top:5px solid #087f8c}}}}</style></head><body><main><pre>{escape(md)}</pre></main></body></html>'''
