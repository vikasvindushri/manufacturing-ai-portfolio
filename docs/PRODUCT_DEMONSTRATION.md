# Product Demonstration

## Objective

Show how the suite converts three common manufacturing workflows into guided, evidence-oriented, and reviewable digital experiences.

## Preparation

1. Run `python -m pytest`.
2. Run `python scripts/check_environment.py`.
3. Start `python -m streamlit run app.py`.
4. Verify that sample data loads in each application.
5. If Gemini is enabled, run `python scripts/test_gemini_connection.py`.

## Quality & 8D Assistant

### Scenario
A torque audit identifies results below the lower limit after tool calibration status became questionable.

### Walkthrough
1. Load the supplied incident.
2. Review normalized facts and missing fields.
3. Generate the governed draft.
4. Inspect the D2 problem statement, D3 containment, D4 hypotheses, and 5-Why prompts.
5. If available, inspect the structured Gemini review.
6. Explain that hypotheses are not confirmed causes.
7. Enter an approver only after evidence review.
8. Download the complete case record.

### Design points
- Deterministic logic creates repeatable structure.
- Gemini adds language reasoning without replacing the local baseline.
- Typed outputs reduce malformed responses.
- Provenance records which path generated the result.
- Human approval remains mandatory for controlled use.

## Manufacturing Knowledge Assistant

### Scenario
A user needs to know what should be checked after a torque-control failure.

### Walkthrough
1. Ask: `What should be checked after a torque failure?`
2. Inspect ranked evidence and relevance scores.
3. Open source expanders and review the exact text.
4. If Gemini is enabled, compare the grounded synthesis with the retrieved evidence.
5. Ask an unrelated question to demonstrate the no-evidence response.

### Design points
- Retrieval and generation are separate stages.
- The application exposes sources rather than hiding them.
- TF-IDF provides a transparent baseline.
- The architecture can later adopt governed embeddings or enterprise search.

## Fault Triage Agent

### Scenario
A hydraulic press reports fluctuating pressure and increased cycle time.

### Walkthrough
1. Load the supplied fault event.
2. Create the triage record.
3. Review category, priority, confidence, likely causes, and diagnostics.
4. Inspect the optional Gemini review.
5. Choose Accept, Modify, or Reject and enter a rationale.
6. Download the action record.
7. Review the workflow schema under `project_3_low_code_agent/workflow/`.

### Design points
- The application organizes first response; it does not control equipment.
- The system never recommends bypassing safeguards.
- The JSON payload supports future workflow and maintenance-system integration.
- Review state is part of the record rather than an informal side conversation.

## Closing summary

The suite combines manufacturing-domain workflow design, transparent automation, optional generative AI, evidence handling, structured outputs, human governance, testing, and an incremental path to enterprise integration.
