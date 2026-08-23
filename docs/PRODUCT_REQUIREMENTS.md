# Product Requirements

## Personas
- Quality engineer responsible for investigation quality and closure.
- Manufacturing engineer responsible for process capability and controls.
- Technician responsible for safe diagnosis and restoration.
- Supervisor responsible for escalation and work coordination.
- Operations leader responsible for adoption, KPI and value realization.

## Functional requirements
- Load synthetic sample input without configuration.
- Validate and normalize input.
- Provide useful local output without Gemini.
- Clearly label hypotheses and confidence.
- Show evidence or provenance.
- Require human review before controlled export.
- Export portable JSON.
- Avoid exposing API keys or confidential data.

## Non-functional requirements
- Usable on a standard laptop browser.
- Graceful behavior when Gemini is unavailable.
- Repeatable tests and CI checks.
- Modular services for future API deployment.
- Accessible labels, readable contrast and concise guidance.
