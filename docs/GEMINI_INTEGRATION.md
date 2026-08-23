# Gemini Integration

## Use by project
- Quality: structured second-pass review identifies missing evidence, hypotheses, 5-Why paths and action candidates.
- RAG: Gemini receives only retrieved chunks and is instructed to answer from that evidence with bracketed references.
- Fault triage: structured second-pass review proposes classification, diagnostic categories and escalation triggers.

## Controls
- Disabled by default.
- API key loaded from environment and excluded by `.gitignore`.
- Low temperature and Pydantic response schemas where structured output is required.
- Local deterministic fallback remains operational.
- Every AI artifact includes provenance and requires a human decision.
- Production implementation should add identity, rate limits, telemetry, redaction, prompt-injection controls and evaluation datasets.
