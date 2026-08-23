# Interview Demo Playbook

## Before the interview
- Run `python -m pytest` and save the passing result.
- Start each app once and verify the sample data loads.
- Confirm Gemini is enabled, or deliberately demonstrate local fallback mode.
- Close unrelated browser tabs and remove confidential material from view.
- Prepare a backup screen recording or screenshots in case network access is blocked.

## Opening narrative
“I approached this as a small manufacturing AI portfolio rather than three disconnected notebooks. Each use case has a named user, workflow, measurable outcome, failure mode, approval gate, and production roadmap.”

## Use case 1: Quality & 8D
### Problem
Quality teams often receive incomplete incidents and spend time creating a consistent investigation structure.

### Demonstration
1. Show the sample incident.
2. Explain the extraction contract and required fields.
3. Generate the draft.
4. Separate observations from hypotheses.
5. Show the evidence-gap list.
6. Show the optional Gemini second-pass review.
7. Record an approval and export.

### What to emphasize
- The local engine is explainable and testable.
- Gemini uses a typed schema, reducing malformed responses.
- The model does not make final root-cause or disposition decisions.
- Production validation would compare completeness, time and expert agreement.

### Likely interview questions
**Why not let the LLM generate the entire 8D?**  
Because the first objective is repeatability and governance. A deterministic scaffold supplies a stable contract; the LLM adds analysis where language reasoning helps.

**How would you prevent hallucinations?**  
Separate facts and hypotheses, provide evidence, constrain outputs, add validation rules, require human approval, log provenance and evaluate unsupported-claim rate.

**How would you integrate with a QMS?**  
Expose a secured API, map fields to the QMS schema, retain source and approval metadata, and create records only after authorization.

## Use case 2: Knowledge Assistant
### Problem
Engineering knowledge is often fragmented, and keyword search may not answer a question in the user's language.

### Demonstration
1. Ask a torque-control question.
2. Inspect retrieved evidence and relevance.
3. Show the grounded answer.
4. Ask an unrelated question to prove refusal/no-evidence behavior.

### What to emphasize
- Retrieval and generation are distinct stages.
- Source references are shown to the user.
- TF-IDF is a transparent baseline; Gemini embeddings or enterprise search are future options.
- Only released, access-controlled documents should enter production retrieval.

## Use case 3: Fault Triage
### Problem
Unstructured fault descriptions cause inconsistent routing and incomplete handoffs.

### Demonstration
1. Submit the hydraulic fault.
2. Show classification, likely causes and checks.
3. Explain the safety disclaimer and escalation logic.
4. Record a reviewer decision.
5. Export the action record and show the low-code schema.

### What to emphasize
- The solution helps organize first response; it does not execute machine control.
- Low-code platforms can collect input and route approvals while Python services handle reusable logic.
- The action payload is designed for a future CMMS/QMS connector.

## Closing statement
“This portfolio shows my approach to industrial AI: start from a measurable workflow, build a transparent baseline, add generative AI only where it improves the experience, preserve human accountability, and design a controlled path from prototype to production.”
